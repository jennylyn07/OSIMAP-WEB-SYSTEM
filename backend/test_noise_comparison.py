#!/usr/bin/env python3
"""Test script to compare noise counts before and after regeneration"""
import json
import os
from pathlib import Path

script_dir = Path(__file__).parent
data_dir = script_dir / "data"
geojson_path = data_dir / "accidents_clustered.geojson"

print("=" * 70)
print("TESTING NOISE COUNT CHANGES AND NEW FEATURES")
print("=" * 70)

# Check if old output exists
if geojson_path.exists():
    print("\n📊 ANALYZING EXISTING OUTPUT (BEFORE REGENERATION)")
    print("-" * 70)
    
    with open(geojson_path, 'r', encoding='utf-8') as f:
        old_geojson = json.load(f)
    
    old_features = old_geojson.get('features', [])
    old_noise = 0
    old_clustered = 0
    old_clusters = set()
    
    for feat in old_features:
        props = feat.get('properties', {})
        if props.get('type') == 'accident_point':
            cluster_id = props.get('cluster', -1)
            if cluster_id == -1:
                old_noise += 1
            else:
                old_clustered += 1
                old_clusters.add(cluster_id)
        elif props.get('type') == 'cluster_center':
            old_clusters.add(props.get('cluster_id'))
    
    print(f"  Old noise points: {old_noise}")
    print(f"  Old clustered points: {old_clustered}")
    print(f"  Old total points: {old_noise + old_clustered}")
    print(f"  Old clusters: {len(old_clusters)}")
    
    # Check for display fields in old output
    old_has_display = False
    for feat in old_features:
        if feat.get('properties', {}).get('type') == 'cluster_center':
            if 'display_center_lat' in feat.get('properties', {}):
                old_has_display = True
                break
    
    print(f"  Old has display fields: {old_has_display}")
    
    # Check for hulls in old output
    old_hull_count = sum(1 for f in old_features if f.get('properties', {}).get('type') == 'cluster_hull')
    print(f"  Old hull polygons: {old_hull_count}")
else:
    print("\n⚠️  No existing output found - will generate fresh")
    old_noise = None
    old_clustered = None
    old_clusters = None
    old_has_display = False
    old_hull_count = 0

# Now run the clustering to regenerate
print("\n" + "=" * 70)
print("REGENERATING CLUSTER OUTPUT")
print("=" * 70)

try:
    import sys
    sys.path.insert(0, str(script_dir))
    from cluster_hdbscan import AccidentClusterAnalyzer
    
    analyzer = AccidentClusterAnalyzer()
    analyzer.main(auto_tune=False, export_alerts=False)
    
    print("\n✅ Clustering completed")
except Exception as e:
    print(f"\n❌ Error running clustering: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Analyze new output
print("\n" + "=" * 70)
print("ANALYZING NEW OUTPUT (AFTER REGENERATION)")
print("-" * 70)

if not geojson_path.exists():
    print("❌ New GeoJSON not found!")
    exit(1)

with open(geojson_path, 'r', encoding='utf-8') as f:
    new_geojson = json.load(f)

new_features = new_geojson.get('features', [])
new_noise = 0
new_clustered = 0
new_clusters = set()
new_cluster_centers = 0
new_hulls = 0
display_fields_present = set()

for feat in new_features:
    props = feat.get('properties', {})
    feat_type = props.get('type')
    
    if feat_type == 'accident_point':
        cluster_id = props.get('cluster', -1)
        if cluster_id == -1:
            new_noise += 1
        else:
            new_clustered += 1
            new_clusters.add(cluster_id)
    elif feat_type == 'cluster_center':
        new_cluster_centers += 1
        new_clusters.add(props.get('cluster_id'))
        # Check for display fields
        for key in props.keys():
            if 'display' in key.lower() or 'radius' in key.lower():
                display_fields_present.add(key)
    elif feat_type == 'cluster_hull':
        new_hulls += 1
        new_clusters.add(props.get('cluster_id'))

print(f"  New noise points: {new_noise}")
print(f"  New clustered points: {new_clustered}")
print(f"  New total points: {new_noise + new_clustered}")
print(f"  New clusters: {len(new_clusters)}")
print(f"  New cluster_center features: {new_cluster_centers}")
print(f"  New hull polygons: {new_hulls}")
print(f"  Display fields found: {sorted(display_fields_present) if display_fields_present else 'None'}")

# Comparison
print("\n" + "=" * 70)
print("COMPARISON RESULTS")
print("=" * 70)

if old_noise is not None:
    noise_diff = new_noise - old_noise
    noise_pct_change = (noise_diff / old_noise * 100) if old_noise > 0 else 0
    
    print(f"\n📈 NOISE COUNT CHANGE:")
    print(f"  Before: {old_noise} noise points")
    print(f"  After:  {new_noise} noise points")
    print(f"  Difference: {noise_diff:+d} ({noise_pct_change:+.2f}%)")
    
    if noise_diff == 0:
        print("  ✓ No change in noise count (expected - only visualization changes)")
    elif noise_diff < 0:
        print(f"  ✓ IMPROVEMENT: {abs(noise_diff)} fewer noise points!")
    else:
        print(f"  ⚠️  INCREASE: {noise_diff} more noise points")
    
    cluster_diff = len(new_clusters) - len(old_clusters)
    print(f"\n📊 CLUSTER COUNT CHANGE:")
    print(f"  Before: {len(old_clusters)} clusters")
    print(f"  After:  {len(new_clusters)} clusters")
    print(f"  Difference: {cluster_diff:+d}")
else:
    print("\n📊 BASELINE (first run):")
    print(f"  Noise points: {new_noise}")
    print(f"  Clustered points: {new_clustered}")
    print(f"  Clusters: {len(new_clusters)}")

# Feature validation
print(f"\n📋 NEW FEATURES VALIDATION:")
required_fields = {'display_center_lat', 'display_center_lon', 'display_radius_m'}
if required_fields.issubset(display_fields_present):
    print("  ✅ All display fields present")
else:
    missing = required_fields - display_fields_present
    print(f"  ❌ Missing: {missing}")

if new_hulls > 0:
    print(f"  ✅ Hull polygons present ({new_hulls} hulls)")
else:
    print("  ❌ No hull polygons found")

# Sample inspection
print(f"\n🔍 SAMPLE INSPECTION:")
for feat in new_features:
    if feat.get('properties', {}).get('type') == 'cluster_center':
        props = feat['properties']
        print(f"  Cluster {props.get('cluster_id')}:")
        print(f"    display_center_lat: {props.get('display_center_lat', 'MISSING')}")
        print(f"    display_center_lon: {props.get('display_center_lon', 'MISSING')}")
        print(f"    display_radius_m: {props.get('display_radius_m', 'MISSING')} m")
        break

hull_samples = 0
for feat in new_features:
    if feat.get('properties', {}).get('type') == 'cluster_hull':
        props = feat['properties']
        geom = feat.get('geometry', {})
        coords = geom.get('coordinates', [])
        ring = coords[0] if coords else []
        print(f"  Hull for cluster {props.get('cluster_id')}: {len(ring)} points")
        hull_samples += 1
        if hull_samples >= 2:
            break

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

all_good = True
if old_noise is not None and noise_diff != 0:
    print("⚠️  Noise count changed - this may indicate clustering parameter changes")
    all_good = False
else:
    print("✓ Noise count unchanged (visualization-only changes confirmed)")

if not required_fields.issubset(display_fields_present):
    print("❌ Display fields missing")
    all_good = False
else:
    print("✓ Display fields present")

if new_hulls == 0:
    print("❌ No hull polygons generated")
    all_good = False
else:
    print(f"✓ Hull polygons generated ({new_hulls} hulls)")

if all_good:
    print("\n✅ ALL TESTS PASSED!")
else:
    print("\n⚠️  SOME ISSUES DETECTED")

print("=" * 70)

