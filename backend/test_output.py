#!/usr/bin/env python3
"""Test script to verify cluster_hdbscan.py output includes hulls and display fields"""
import json
import os
from pathlib import Path

# Paths
script_dir = Path(__file__).parent
data_dir = script_dir / "data"
geojson_path = data_dir / "accidents_clustered.geojson"
cluster_centers_path = data_dir / "cluster_centers.json"

print("=" * 60)
print("TESTING CLUSTER OUTPUT")
print("=" * 60)

# Check if files exist
if not geojson_path.exists():
    print(f"❌ GeoJSON not found: {geojson_path}")
    print("   Run cluster_hdbscan.py first to generate output")
    exit(1)

print(f"\n✓ Found GeoJSON: {geojson_path}")

# Load and analyze GeoJSON
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
        # Check geometry
        geom = feat.get('geometry', {})
        if geom.get('type') == 'Polygon':
            coords = geom.get('coordinates', [])
            if coords and len(coords[0]) >= 3:
                print(f"  ✓ Hull for cluster {cid}: {len(coords[0])} points")

print(f"\n--- Feature Type Counts ---")
for typ, count in sorted(type_counts.items()):
    print(f"  {typ}: {count}")

print(f"\n--- Display Fields in cluster_center ---")
if display_fields_found:
    for field in sorted(display_fields_found):
        print(f"  ✓ {field}")
else:
    print("  ❌ No display fields found!")

print(f"\n--- Cluster Coverage ---")
print(f"  Clusters with centers: {len(cluster_ids_with_centers)}")
print(f"  Clusters with hulls: {len(cluster_ids_with_hulls)}")

# Check if all clusters have both
missing_hulls = cluster_ids_with_centers - cluster_ids_with_hulls
missing_centers = cluster_ids_with_hulls - cluster_ids_with_centers

if missing_hulls:
    print(f"  ⚠️  Clusters missing hulls: {sorted(missing_hulls)}")
if missing_centers:
    print(f"  ⚠️  Clusters missing centers: {sorted(missing_centers)}")

# Sample a cluster_center to show fields
print(f"\n--- Sample cluster_center Properties ---")
for feat in features:
    if feat.get('properties', {}).get('type') == 'cluster_center':
        props = feat['properties']
        print(f"  Cluster ID: {props.get('cluster_id')}")
        print(f"  Center (mean): {props.get('center_lat'):.6f}, {props.get('center_lon'):.6f}")
        if 'display_center_lat' in props:
            print(f"  Display center: {props.get('display_center_lat'):.6f}, {props.get('display_center_lon'):.6f}")
        if 'display_radius_m' in props:
            print(f"  Display radius: {props.get('display_radius_m'):.2f} m")
        print(f"  Danger score: {props.get('danger_score')}")
        print(f"  Accident count: {props.get('accident_count')}")
        break

# Sample a cluster_hull to show structure
print(f"\n--- Sample cluster_hull Geometry ---")
for feat in features:
    if feat.get('properties', {}).get('type') == 'cluster_hull':
        props = feat['properties']
        geom = feat.get('geometry', {})
        print(f"  Cluster ID: {props.get('cluster_id')}")
        print(f"  Geometry type: {geom.get('type')}")
        coords = geom.get('coordinates', [])
        if coords:
            ring = coords[0]
            print(f"  Polygon points: {len(ring)}")
            print(f"  First point: {ring[0]}")
            print(f"  Last point: {ring[-1]}")
        break

# Final validation
print(f"\n--- Validation Summary ---")
all_good = True

if 'cluster_center' not in type_counts:
    print("❌ No cluster_center features found")
    all_good = False
else:
    print("✓ cluster_center features present")

if 'cluster_hull' not in type_counts:
    print("❌ No cluster_hull features found")
    all_good = False
else:
    print("✓ cluster_hull features present")

if not display_fields_found:
    print("❌ No display_* fields found in cluster_center")
    all_good = False
else:
    required = {'display_center_lat', 'display_center_lon', 'display_radius_m'}
    if required.issubset(display_fields_found):
        print("✓ All required display fields present")
    else:
        missing = required - display_fields_found
        print(f"❌ Missing display fields: {missing}")
        all_good = False

if all_good:
    print("\n✅ ALL TESTS PASSED - Output looks correct!")
else:
    print("\n⚠️  SOME TESTS FAILED - Check output above")

print("=" * 60)

