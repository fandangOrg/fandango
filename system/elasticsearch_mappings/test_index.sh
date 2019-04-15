#!/bin/bash

# note the \" escaping on quotations inside -d argument

curl -XPUT 'localhost:9220/test?pretty' -d " 
{
  \"mappings\": {
    \"user\": { 
      \"_all\":       { \"enabled\": false  }, 
      \"properties\": { 
        \"title\":    { \"type\": \"text\"  }, 
        \"name\":     { \"type\": \"text\"  }, 
        \"age\":      { \"type\": \"integer\" }  
      }
    },
    \"blogpost\": { 
      \"_all\":       { \"enabled\": false  }, 
      \"properties\": { 
        \"title\":    { \"type\": \"text\"  }, 
        \"body\":     { \"type\": \"text\"  }, 
        \"user_id\":  {
          \"type\":   \"keyword\" 
        },
        \"created\":  {
          \"type\":   \"date\", 
          \"format\": \"strict_date_optional_time||epoch_millis\"
        }
      }
    }
  }
}"
