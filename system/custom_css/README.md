# Siren Investigate White Labeling

## OVERVIEW
This is an example of Investigate plugin to override css values without modifying the source code of Investigate.

## STEPS
-Extract or Clone to /siren-investigate/plugins/ folder.
-Empty /siren-investigate/optimize/ folder.
-Edit CSS style in /siren-investigate/plugins/custom_css/public/less/custom.less
-(Re)start Siren Investigate /siren-investigate/bin/investigate

## NOTES
The less file contains examples of how to override styles from investigate. 
To override specific styles, locate the css style property in Chrome Dev Tools inspector and override it here using  "!important;"


