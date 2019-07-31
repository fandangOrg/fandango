export interface Button {
    type: string;
    name: string;
    icon: string;
    placeholder: string;
    input: string;
    description: string;
}

export const Buttons = [
    {
        type: 'article',
        name: 'Article',
        icon: 'far fa-newspaper',
        placeholder: 'Article URL',
        input: 'url',
        description: 'CHECK THE TRUSTWORTHINESS OF AN ARTICLE AND ITS METADATA'
    },
    {
        type: 'image',
        name: 'Image',
        icon: 'fas fa-image',
        placeholder: 'Image URL',
        input: 'url',
        description: 'CHECK IF AN IMAGE HAS BEEN MODIFIED OR HAS A WRONG TAG'
    },
    {
        type: 'video',
        name: 'Video',
        icon: 'fas fa-video',
        placeholder: 'Video URL',
        input: 'url',
        description: 'CHECK IF A VIDEO HAS BEEN MODIFIED OR HAS A WRONG TAG'
    },
    {
        type: 'claim',
        name: 'Claim',
        icon: 'fas fa-font',
        placeholder: 'Sentence',
        input: 'text',
        description: 'RETRIEVE MOST SIMILAR CLAIMS'
    }
];

export var sirenUrl = 'http://40.114.234.51:8080/app/kibana#/dashboard/dashboard:ae5adc20-7332-11e9-bc6e-fd20d0a34816?_a=(columns:!(about,about.keyword,articleBody,articleBody.keyword,author,calculatedRating,contains,dateModified,datePublished,headline,headline.keyword,identifier,mentions,publisher,dateCreated,calculatedRatingDetail,sourceDomain),description:\'\',filters:!((\'$state\':(store:appState),meta:(alias:\'Filter%20by%20ID\',disabled:!f,index:\'index-pattern:bde38330-682a-11e9-9dbd-2f9b58e9a9bb\',key:identifier,negate:!f,type:phrase,value:\'0df7f440a6569f78124795a2ff12d575\'),query:(match:(identifier:(query:\'QUERYDACAMBIARE\',type:phrase))))),id:\'dashboard:ae5adc20-7332-11e9-bc6e-fd20d0a34816\',index:\'index-pattern:bde38330-682a-11e9-9dbd-2f9b58e9a9bb\',interval:auto,options:(darkTheme:!f,hideBorders:!f),panels:!((col:1,id:\'visualization:ae2f1130-7332-11e9-bc6e-fd20d0a34816\',panelIndex:1,row:1,size_x:12,size_y:3,type:visualization),(col:1,id:\'visualization:ae2eea20-7332-11e9-bc6e-fd20d0a34816\',panelIndex:2,row:4,size_x:12,size_y:3,type:visualization),(col:1,id:\'visualization:ae3c57a0-7332-11e9-bc6e-fd20d0a34816\',panelIndex:3,row:7,size_x:9,size_y:3,type:visualization),(col:10,id:\'visualization:ae201d10-7332-11e9-bc6e-fd20d0a34816\',panelIndex:4,row:7,size_x:3,size_y:3,type:visualization),(col:1,id:\'visualization:ae206b30-7332-11e9-bc6e-fd20d0a34816\',panelIndex:5,row:10,size_x:4,size_y:2,type:visualization),(col:5,id:\'visualization:ae20b950-7332-11e9-bc6e-fd20d0a34816\',panelIndex:6,row:10,size_x:4,size_y:2,type:visualization),(col:9,id:\'visualization:ae20e060-7332-11e9-bc6e-fd20d0a34816\',panelIndex:7,row:10,size_x:4,size_y:2,type:visualization),(col:1,id:\'visualization:ae210770-7332-11e9-bc6e-fd20d0a34816\',panelIndex:8,row:12,size_x:4,size_y:2,type:visualization),(col:5,id:\'visualization:ae23c690-7332-11e9-bc6e-fd20d0a34816\',panelIndex:9,row:12,size_x:4,size_y:2,type:visualization),(col:9,id:\'visualization:ae2c2b00-7332-11e9-bc6e-fd20d0a34816\',panelIndex:10,row:12,size_x:4,size_y:2,type:visualization),(col:1,id:\'visualization:ae2f8660-7332-11e9-bc6e-fd20d0a34816\',panelIndex:11,row:14,size_x:4,size_y:2,type:visualization),(col:5,id:\'visualization:ae3049b0-7332-11e9-bc6e-fd20d0a34816\',panelIndex:12,row:14,size_x:4,size_y:2,type:visualization),(col:9,id:\'visualization:ae3b1f20-7332-11e9-bc6e-fd20d0a34816\',panelIndex:13,row:14,size_x:4,size_y:2,type:visualization),(col:1,id:\'visualization:ae3cccd0-7332-11e9-bc6e-fd20d0a34816\',panelIndex:14,row:16,size_x:4,size_y:2,type:visualization),(col:5,id:\'visualization:ae3bbb60-7332-11e9-bc6e-fd20d0a34816\',panelIndex:15,row:16,size_x:4,size_y:2,type:visualization),(col:9,id:\'visualization:ae424b10-7332-11e9-bc6e-fd20d0a34816\',panelIndex:16,row:16,size_x:4,size_y:2,type:visualization),(col:1,id:\'visualization:ae4ea720-7332-11e9-bc6e-fd20d0a34816\',panelIndex:17,row:18,size_x:12,size_y:3,type:visualization)),query:(match_all:()),sort:!(dateCreated,desc),timeRestore:!t,title:Articles,uiState:(quickState:(addedSavedSearches:!(),addedSavedVises:!(\'visualization:ae201d10-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae206b30-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae20b950-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae20e060-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae210770-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae23c690-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae2c2b00-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae2f1130-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae2eea20-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae2f8660-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae3049b0-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae3b1f20-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae3cccd0-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae3bbb60-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae3c57a0-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae424b10-7332-11e9-bc6e-fd20d0a34816\',\'visualization:ae4ea720-7332-11e9-bc6e-fd20d0a34816\'),quickId:\'0f0ff561-dbec-4722-bb35-9193e2034f60\')),viewMode:view)&_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:now-15y,mode:relative,to:now))&_k=(d:(\'dashboard:01a7b330-682f-11e9-9d8a-918e2b017a18\':(t:(f:now-15y,m:relative,t:now)),\'dashboard:51075490-682e-11e9-9d8a-918e2b017a18\':(t:(f:now-15y,m:relative,t:now)),\'dashboard:ae5adc20-7332-11e9-bc6e-fd20d0a34816\':(t:(f:now-15y,m:relative,t:now)),\'dashboard:c34d48f0-732f-11e9-bc6e-fd20d0a34816\':(t:(f:now-15y,m:relative,t:now)),\'dashboard:dea64020-683a-11e9-9d8a-918e2b017a18\':(t:(f:now-15y,m:relative,t:now)),\'dashboard:eeb80520-683a-11e9-9d8a-918e2b017a18\':(t:(f:now-15y,m:relative,t:now))))';