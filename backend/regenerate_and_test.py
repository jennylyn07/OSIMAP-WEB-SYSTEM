#!/usr/bin/env python3
"""Regenerate cluster output and test it"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cluster_hdbscan import AccidentClusterAnalyzer
import json

print("=" * 60)
print("REGENERATING CLUSTER OUTPUT WITH NEW FEATURES")
print("=" * 60)

# Run the analyzer
analyzer = AccidentClusterAnalyzer()
analyzer.main(auto_tune=False, export_alerts=True)

print("\n" + "=" * 60)
print("TESTING OUTPUT")
print("=" * 60)

# Now test the output
from pathlib import Path
data_dir = Path(__file__).parent / "data"
geojson_path = data_dir / "accidents_clustered.geojson"

if not geojson_path.exists():
    print(f"❌ GeoJSON not found: {geojson_path}")
    sys.exit(1)

with open(geojson_path, 'r', encoding='utf-8') as f:
    geojson = json.load(f)

features = geojson.get('features', [])
print(f"\nTotal features: {len(features)}")

# Count by type
type_counts = {}
display_fields_found = set()
cluster_ids_with_hulls = set()
cluster_ids_with_centers = set()

for feat in features:
    props = feat.get('properties', {})
    feat_type = props.get('type', 'unknown')
    type_counts[feat_type] = type_counts.get(feat_type, 0) + 1
    
    if feat_type == 'cluster_center':
        cid = props.get('cluster_id')
        if cid is not None:
            cluster_ids_with_centers.add(cid)
        # Check for display fields
        for key in props.keys():
            if 'display' in key.lower() or 'radius' in key.lower():
                display_fields_found.add(key)
    
    if feat_type == 'cluster_hull':
        cid = props.get('cluster_id')
        if cid is not None:
            cluster_ids_with_hulls.add(cid)

print(f"\n--- Feature Type Counts ---")
for typ, count in sorted(type_counts.items()):
    print(f"  {typ}: {count}")

print(f"\n--- Display Fields Found ---")
if display_fields_found:
    for field in sorted(display_fields_found):
        print(f"  ✓ {field}")
else:
    print("  ❌ No display fields found!")

print(f"\n--- Cluster Coverage ---")
print(f"  Clusters with centers: {len(cluster_ids_with_centers)}")
print(f"  Clusters with hulls: {len(cluster_ids_with_hulls)}")

# Sample inspection
print(f"\n--- Sample cluster_center ---")
for feat in features:
    if feat.get('properties', {}).get('type') == 'cluster_center':
        props = feat['properties']
        print(f"  Cluster {props.get('cluster_id')}:")
        print(f"    display_center_lat: {props.get('display_center_lat', 'MISSING')}")
        print(f"    display_center_lon: {props.get('display_center_lon', 'MISSING')}")
        print(f"    display_radius_m: {props.get('display_radius_m', 'MISSING')}")
        break

print(f"\n--- Sample cluster_hull ---")
hull_count = 0
for feat in features:
    if feat.get('properties', {}).get('type') == 'cluster_hull':
        hull_count += 1
        if hull_count == 1:
            props = feat['properties']
            geom = feat.get('geometry', {})
            print(f"  Cluster {props.get('cluster_id')}:")
            print(f"    Geometry type: {geom.get('type')}")
            coords = geom.get('coordinates', [])
            if coords:
                ring = coords[0] if coords else []
                print(f"    Polygon points: {len(ring)}")
        if hull_count >= 3:
            break

if hull_count == 0:
    print("  ❌ No hulls found!")

# Final validation
print(f"\n--- Validation ---")
all_good = True

if 'cluster_hull' not in type_counts:
    print("❌ FAIL: No cluster_hull features")
    all_good = False
else:
    print(f"✓ PASS: {type_counts['cluster_hull']} cluster_hull features")

required_fields = {'display_center_lat', 'display_center_lon', 'display_radius_m'}
if not required_fields.issubset(display_fields_found):
    missing = required_fields - display_fields_found
    print(f"❌ FAIL: Missing fields: {missing}")
    all_good = False
else:
    print("✓ PASS: All display fields present")

if all_good:
    print("\n✅ ALL TESTS PASSED!")
else:
    print("\n⚠️  SOME TESTS FAILED")

print("=" * 60)

