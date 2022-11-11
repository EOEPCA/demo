
# Data Management Demonstration Script

## Resource Catalogue

* Show 'Collections' for Sentinel-2 and Landsat-8
  
* Sentinel-2 MSI Level 2A -> items
  * Footprints of the listed scenes are shown on the map
  * Map can be panned and zoomed
  * Scenes can be selected on map
  * Select the first scene for more details
  * Select for JSON representation

* Select Landsat-8 Level 1TP -> items
  * show some details

* Highlight the different endpoints for:
  * OGC API Records (default)
  * CSW 2.0.2/3.0
  * OpenSearch
  * STAC

## Data Access

* Pan & Zoom
  * Zoom out to see scenes over central europe

* Timeslider
  * Select dot 'Aug 05' to zoom map to scene
  * Re-crop time to Aug 05
  * Hover over dot Aug 29 to highlight other scenes on map
  * Move time to Aug 29

* Click scene on map
  * 'i' to get more details
    * Observe WCS access details for bands
      * select DescribeCoverage for Band 1
    * Observer metadata, e.g. cloud coverage
  * '+' to add to basket
  * '-' to remove from basket

* Search results
  * Hover scene to highlight on map
  * Click scene to add to basket
  * 'i' to get more details

* Basket
  * Download as URL lists
  * Download product
    * Download multiple files
    * Draw Bounding Box = small rectangle
    * Projection = WGS-84
    * Package = ZIP
    * Format = TIFF
    * Scale = 20%
  * Deselect all

* Filter
  * Re-select all of August on timeslider
  * Deselect L8 1GT layer
  * Filters -> clear selection
  * Select Filters -> Cloud Coverage 0-20%
    * Observe reduced search results
    * Reset cloud coverage -> 100%
  * Select Rectangle filter
    * small area over lake bottom right
    * 'i' to see scene details
    * clear selection

* Layers
  * Re-select all of August on timeslider
  * Turn off Landsat-8 layers
  * Turn on Sentinel-2 Level 2A layer
    * Also turn on in the Search Results

## Harvesting

### Resource Catalogue

* Collection `L8MSI1TP`
  * Observe that we now have records over the UK

### Data Access

* Map shows records over the UK
* Select date range to cover 11 Aug
* Get detailed info for image
