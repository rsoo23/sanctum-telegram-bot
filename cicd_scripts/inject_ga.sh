#!/bin/bash

# Define the path to your index.html file
FILE="Game/build-templates/web-mobile/index.ejs"

# Check the environment variable
if [ "$ENV" == "production" ]; then
  # GA_ID=$GA_ID_PRODUCTION
  sed -i '' "s/G-XXXXXXXXXX/$GA_ID/g" $FILE
else
  # GA_ID=$GA_ID_STAGING
  sed -i '' "s/G-XXXXXXXXXX/$GA_ID/g" $FILE
fi


echo "Injected Google Analytics ID ($GA_ID) into index.ejs"
