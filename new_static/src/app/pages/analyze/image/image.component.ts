import {Component, EventEmitter, OnInit, Output} from '@angular/core';

@Component({
  selector: 'app-image',
  templateUrl: './image.component.html',
  styleUrls: ['./image.component.scss']
})
export class ImageComponent implements OnInit {

    @Output() showLoading = new EventEmitter<boolean>();

    constructor() { }

  ngOnInit() {
      this.showLoading.emit(false);
  }

}
