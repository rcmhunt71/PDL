## REQUIREMENTS:
This are the **identified** requirements for each piece of the process. This document will be used to determine the required architecture, classes, interfaces, and restrictions.

## SELECT URLS
1. Verify URLs are token-delimited (space)
   1. Split if https:// is found in the middle of the string.
   1. Debug log that action is occurring.
   1. Debug log any records that were acted on.
1. Remove duplicates from list
   1. Cast: `list(set(url_list))`
      1. Debug log how many duplicates were found
      1. Debug log which urls were duplicates? 


## DETERMINE IMAGE URL
1. Find largest image URL

  
## DOWNLOAD IMAGE
1. Determine if image has been downloaded:
   1. Locally:
      1. Check local file system
   1. Remotely:
      1. Data repository of images
      1. Download image to local storage
	  1. Parallel downloads
	  1. Record time per DL
1. Monitor and report status 
   1. ERROR or TIMEOUT: retry
   1. Backoff retry mechanism
  	    
	
## STATISTICS
1. Number of duplicates in the DL list
1. Number of splits in the DL list?
1. Number of Images:
   1. Downloaded
   1. Skipped 
      1. Local
      1. Remote 
   1. Errored
   1. Total time to download
   1. Avg time to download
		
		
## CLI
1. Dry-run
1. Utilities execution
1. Help screens and logical options/descriptions
1. Specify logging level
1. Mount-check for specific options

		
## OUTPUT 
1. Log to screen (debug or info)
1. Log to file
1. Create summary file per execution
   1. Unique filename
   1. Replay ability
   1. Store in common directory


## DATA REPOSITORY
1. Autostart service if not running
1. Persistent
1. Data Fields
   1. Image Name
   1. Image URL
   1. Web URL
   1. Photographer
   1. Size
   1. Storage Locations 
   1. Subject Name 
   1. DL Date

  	  
## UTILITIES
1. Data Repository | Disk Sync
1. Duplicate Check
1. Stats generator
1. Log | Data sync
1. Report generation

	  
## VISUAL CLASSIFICATION/SORTING
1. Classifications
1. Locations
1. Viewer
   1. Zoom
   1. Panels
   1. Options    

	   
## UNIT TESTS
1. PyTest
   1. Coverage Metrics
   1. Mocks

		  
## REPOSITORIES 
1. [PDL](https://github.com/rcmhunt71/PDL)

	  
## INSTALLATION: 
1. pip installable
