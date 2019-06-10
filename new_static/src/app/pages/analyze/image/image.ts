export class Image {
    score: number;
    details?: object[];
    size: string;
    url: string;
    format: string;
    id: string;
    status: string;
    type: string;
    date: string;


    constructor(score: number, details: object[], size: string, url: string, format: string, id: string, status: string, type: string, date: string) {
        this.score = score;
        this.details = details;
        this.size = size;
        this.url = url;
        this.format = format;
        this.id = id;
        this.status = status;
        this.type = type;
        this.date = date;
    }
}
