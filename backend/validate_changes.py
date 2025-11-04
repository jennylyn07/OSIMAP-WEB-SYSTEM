#!/usr/bin/env python3
"""Simple validation script - run after regenerating cluster output"""
import json
from pathlib import Path

data_dir = Path(__file__).parent / "data"
geojson_path = data_dir / "accidents_clustered.geojson"

print("=" * 70)
print("VALIDATING CLUSTER OUTPUT CHANGES")
print("=" * 70)

# Baseline from old output (before my changes)
OLD_NOISE = 6330
OLD_CLUSTERED = 7095
OLD_CLUSTERS = 36

if not geojson_path.exists():
    print(f"❌ GeoJSON not found: {geojson_path}")
    print("   Run: python backend/cluster_hdbscan.py")
    exit(1)

with open(geojson_path, 'r', encoding='utf-8') as f:
    geojson = json.load(f)

features = geojson.get('features', [])
noise = 0
clustered = 0
clusters = set()
cluster_centers = 0
hulls = 0
display_fields = set()

for feat in features:
    props = feat.get('properties', {})
    feat_type = props.get('type')
    
    if feat_type == 'accident_point':
        cid = props.get('cluster', -1)
        if cid == -1:
            noise += 1
        else:
            clustered += 1
            clusters.add(cid)
    elif feat_type == 'cluster_center':
        cluster_centers += 1
        clusters.add(props.get('cluster_id'))
        for key in props.keys():
            if 'display' in key.lower() or 'radius' in key.lower():
                display_fields.add(key)
    elif feat_type == 'cluster_hull':
        hulls += 1
        clusters.add(props.get('cluster_id'))

print(f"\n📊 NOISE COUNT ANALYSIS:")
print(f"  Old noise: {OLD_NOISE}")
print(f"  New noise: {noise}")
print(f"  Change: {noise - OLD_NOISE:+d}")

if noise == OLD_NOISE:
    print("  ✅ NO CHANGE - Expected (only visualization features added)")
else:
    print(f"  ⚠️  CHANGED - This may indicate clustering parameter changes")

print(f"\n📊 CLUSTER COUNT:")
print(f"  Old clusters: {OLD_CLUSTERS}")
print(f"  New clusters: {len(clusters)}")
print(f"  Change: {len(clusters) - OLD_CLUSTERS:+d}")

print(f"\n📋 NEW FEATURES:")
print(f"  Cluster centers: {cluster_centers}")
print(f"  Hull polygons: {hulls}")

required_fields = {'display_center_lat', 'display_center_lon', 'display_radius_m'}
print(f"\n  Display fields:")
for field in sorted(display_fields):
    status = "✅" if field in required_fields else "ℹ️"
    print(f"    {status} {field}")

if not required_fields.issubset(display_fields):
    missing = required_fields - display_fields
    print(f"    ❌ Missing: {missing}")

print(f"\n✅ VALIDATION:")
all_good = True

if noise != OLD_NOISE:
    print("  ⚠️  Noise count changed")
    all_good = False
else:
    print("  ✓ Noise count unchanged (expected)")

if not required_fields.issubset(display_fields):
    print("  ❌ Missing display fields")
    all_good = False
else:
    print("  ✓ Display fields present")

if hulls == 0:
    print("  ❌ No hull polygons")
    all_good = False
else:
    print(f"  ✓ Hull polygons present ({hulls} hulls)")

# Sample output
print(f"\n🔍 SAMPLE CLUSTER CENTER:")
for feat in features:
    if feat.get('properties', {}).get('type') == 'cluster_center':
        props = feat['properties']
        print(f"  Cluster {props.get('cluster_id')}:")
        print(f"    display_center_lat: {props.get('display_center_lat', 'MISSING')}")
        print(f"    display_center_lon: {props.get('display_center_lon', 'MISSING')}")
        print(f"    display_radius_m: {props.get('display_radius_m', 'MISSING')} m")
        break

print(f"\n🔍 SAMPLE HULL:")
hull_count = 0
for feat in features:
    if feat.get('properties', {}).get('type') == 'cluster_hull':
        props = feat['properties']
        geom = feat.get('geometry', {})
        coords = geom.get('coordinates', [])
        ring = coords[0] if coords else []
        print(f"  Cluster {props.get('cluster_id')}: {len(ring)} polygon points")
        hull_count += 1
        if hull_count >= 2:
            break

if hull_count == 0:
    print("  ❌ No hulls found")

print("\n" + "=" * 70)
if all_good:
    print("✅ ALL VALIDATIONS PASSED")
    print("\nThe solution is working correctly:")
    print("  • Noise count unchanged (no clustering algorithm changes)")
    print("  • Display fields added for better visualization")
    print("  • Hull polygons added for accurate cluster boundaries")
else:
    print("⚠️  SOME VALIDATIONS FAILED")
print("=" * 70)

