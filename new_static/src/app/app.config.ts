export interface Button {
    type: string;
    name: string;
    icon: string;
    placeholder: string;
    input: string;
    description: string;
}

export const ImageInfoLabels = [
    {
        key: 'CopyMove',
        value: 'Has a part of this image been copy-pasted over another area? Red shows areas with high probability of a pasted object, Green shows areas with high probability of copied object,Blue shows areas with a low probability of any manipulation.'
    },
    {
        key: 'Splicing',
        value: 'Has an object of another unknown image been pasted over this one? Red shows areas with high probability of a pasted object, Blue shows areas with low probability of a pasted object.'
    },
    {
        key: 'Manipulation',
        value: 'Has an area of the image been altered in any way? Red shows areas with high probability of manipulation, Blue shows areas with low probability of manipulation.'
    }
    , {
        key: 'faceForensics',
        value: ' Has a face shown in this image been manipulated, or is it a deep-fake? All detected faces have a box surrounding them. If the box is Red, there is high probability that the face is manipulated while if the box is Blue the face is probably original.'
    }
];

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
