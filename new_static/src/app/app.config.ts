export interface Button {
    type: string;
    name: string;
    icon?: string;
    useImage?: string;
    placeholder: string;
    description: string;
}

export const Buttons = [
    {
        type: 'article',
        name: 'Article',
        icon: 'far fa-newspaper',
        placeholder: 'Article URL',
        description: 'CHECK THE TRUSTWORTHINESS OF AN ARTICLE AND ITS METADATA'
    },
    {
        type: 'image',
        name: 'Image',
        icon: 'fas fa-image',
        placeholder: 'Image URL',
        description: 'CHECK IF AN IMAGE HAS BEEN MODIFIED OR HAVE A WRONG TAG'
    },
    {
        type: 'video',
        name: 'Video',
        icon: 'fas fa-video',
        placeholder: 'Video URL',
        description: 'CHECK IF  A VIDEO HAS BEEN MODIFIED OR HAVE A WRONG TAG'
    },
    {
        type: 'claim',
        name: 'Claim',
        icon: 'fas fa-font',
        placeholder: 'URL or a sentence',
        description: 'RETRIEVE MOST SIMILAR CLAIMS'
    }
    // {
    //     type: 'siren',
    //     name: 'Siren',
    //     useImage: 'assets/img/logos/siren.png',
    //     placeholder: 'Siren URL',
    //     description: ''
    // }
];
