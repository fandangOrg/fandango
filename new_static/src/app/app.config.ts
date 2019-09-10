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

export var sirenUrl = 'http://40.114.234.51:8080/app/kibana#/dashboard/dashboard:dfd89820-a710-11e9-ba65-afa368009f5e?_a=(description:\'\',filters:!((\'$state\':(store:appState),meta:(alias:!n,disabled:!f,index:\'index-pattern:784d2c90-a3c1-11e9-a978-5fe038f83f3f\',key:url,negate:!f,type:phrase,value:\'QUERYDACAMBIARE\'),query:(match:(url:(query:\'QUERYDACAMBIARE\',type:phrase))))),id:\'dashboard:dfd89820-a710-11e9-ba65-afa368009f5e\',options:(darkTheme:!f,hideBorders:!f,showTimePicker:!t))';
