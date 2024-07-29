#!/bin/bash

# Define the path to your index.html file
FILE="Game/build-templates/web-mobile/index.ejs"

# Check the environment variable
# if [ "$ENV" == "production" ]; then
#   GA_ID=$GA_ID_PRODUCTION
# else
#   GA_ID=$GA_ID_STAGING
# fi

# Replace the placeholders with the actual Google Analytics ID
sed -i '' "s/G-XXXXXXXXXX/$GA_ID/g" $FILE

echo "Injected Google Analytics ID ($GA_ID) into index.html"
