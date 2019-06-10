export class Article {
    identified: string;
    language: string;
    headline: string;
    body: string;
    images: string[];
    videos: string[];
    publishers: object[];
    authors: object[];
    textAnalysis: object[];
    similarNews: object[];

    constructor(identified: string, language: string, headline: string, body: string, images: string[], videos: string[], publishers: object[], authors: object[], textAnalysis: object[], similarNews: object[]) {
        this.identified = identified;
        this.language = language;
        this.headline = headline;
        this.body = body;
        this.images = images;
        this.videos = videos;
        this.publishers = publishers;
        this.authors = authors;
        this.textAnalysis = textAnalysis;
        this.similarNews = similarNews;
    }
}

