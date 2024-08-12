var shadowWater = ee.FeatureCollection('projects/ee-efjustiniano/assets/doutorado/waterIndex/shadowWater')
var rectangle = ee.FeatureCollection('projects/ee-efjustiniano/assets/doutorado/waterIndex/waterShadowRectangle')

Map.addLayer(shadowWater, false, 'polygons of water and non-water', false)
Map.addLayer(rectangle, false, 'ROI', false)

var S2 = ee.ImageCollection('projects/ee-efjustiniano/assets/doutorado/waterIndex/cities_harmonized')
  .select(['B2', 'B3', 'B4', 'B8', 'B11', 'B12'])
  .median()
  .reproject({
      crs: 'EPSG:4326',
      scale: 10
    })
  .clip(rectangle)
  .divide(10000)
;

Map.addLayer(S2, {bands: ["B3","B8","B11"], gamma: 1, min: 0.0065, max:0.4196, opacity:1}, 'Sentinel 3 8 11', false);
var line = ee.Image().paint(shadowWater,0,0.2);

Map.addLayer(line, {palette: ['red']}, 'Water');

var randomPoints = ee.FeatureCollection('projects/ee-efjustiniano/assets/doutorado/waterIndex/shadowWaterPoints_20231123')
  .select('city', 'surface', 'classWat')
//Map.addLayer(randomPoints, {color:'red'}, 'points')

var water = randomPoints.filter(ee.Filter.eq('surface', 'water'))
Map.addLayer(water, {color: 'cyan'}, 'water points')

var nonWater = randomPoints.filter(ee.Filter.eq('surface', 'non-water'))
Map.addLayer(nonWater, {color: 'red'}, 'non-water points', false)

var sample = S2.sampleRegions({
  collection: randomPoints,
  geometries: true,
  scale: 10
});

print(S2)

Export.table.toDrive({
  collection: ee.FeatureCollection(sample),
  description: 'samplePointsCities_20240811_harmonized',
  fileFormat: 'CSV',
  folder: 'water',
  selectors: ['B2', 'B3', 'B4', 'B8', 'B11', 'B12', 'city', 'surface', 'classWat']
});
