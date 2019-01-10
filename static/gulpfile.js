'use strict';

var gulp = require('gulp'),
    watch = require('gulp-watch'),
    prefixer = require('gulp-autoprefixer'),
    cssmin = require('gulp-cssmin'),
    rename = require('gulp-rename'),
    concat = require('gulp-concat'),
    uncss = require('gulp-uncss'),
    uglify = require('gulp-uglify'),
    rimraf = require('rimraf'),
    browserSync = require('browser-sync').create();

var path = {
    source: {
        html: 'source/html/*.html',
        html_partials: 'source/html/html_partials/**/*.html',
        js: 'source/js/**/*.js',
        css: 'source/css/**/*.css',
        img: 'source/img/**/*.*',
        libs: 'source/libs/**/*.*'
    },
    dist: {
        html: 'dist/',
        js: 'dist/js/',
        css: 'dist/css/',
        img: 'dist/img/',
        libs: 'dist/libs/'
    },
    watch: {
        html: 'source/html/**/*.*',
        html_partials: 'source/html/html_partials/**/*.html',
        js: 'source/js/**/*.js',
        css: 'source/css/**/*.css',
        img: 'source/img/**/*.*',
        libs: 'source/libs/**/*.*'
    }
};

gulp.task('html:build', function () {
    gulp.src(path.source.html)
        .pipe(gulp.dest(path.dist.html))
        .pipe(browserSync.reload({stream: true}));

});

gulp.task('html_partials:build', function () {
    gulp.src(path.source.html_partials)
        .pipe(rename({dirname: ''}))
        .pipe(gulp.dest(path.dist.html))
        .pipe(browserSync.reload({stream: true}));

});

gulp.task('js:build', function () {
    gulp.src(path.source.js)
        .pipe(uglify())
        .pipe(rename({suffix: '.min'}))
        .pipe(gulp.dest(path.dist.js))
        .pipe(browserSync.reload({stream: true}));
});

gulp.task('css:build', function () {
    gulp.src(path.source.css)
        // .pipe(uncss({
        //     html: ['source/html/*.html', 'source/html_partials/*.html']
        // }))
        .pipe(cssmin())
        .pipe(prefixer('last 2 version', 'safari 5', 'ie 8', 'ie 9'))
        .pipe(concat('style.min.css'))
        .pipe(gulp.dest(path.dist.css))
        .pipe(browserSync.reload({stream: true}));
});

gulp.task('libs:build', function () {
    gulp.src(path.source.libs)
        .pipe(gulp.dest(path.dist.libs))
        .pipe(browserSync.reload({stream: true}));

});

gulp.task('image:build', function () {
    gulp.src(path.source.img)
        .pipe(gulp.dest(path.dist.img))
});


gulp.task('clean', function (cb) {
    rimraf('./dist', cb);
});

gulp.task('build', [
    'js:build',
    'css:build',
    'libs:build',
    'image:build',
    'html:build',
    'html_partials:build'
]);

gulp.task('watch', function () {
    watch([path.watch.html], function (event, cb) {
        gulp.start('html:build');
    });
    watch([path.watch.html_partials], function (event, cb) {
        gulp.start('html_partials:build');
    });
    watch([path.watch.css], function (event, cb) {
        gulp.start('css:build');
    });
    watch([path.watch.js], function (event, cb) {
        gulp.start('js:build');
    });
    watch([path.watch.libs], function (event, cb) {
        gulp.start('libs:build');
    });
    watch([path.watch.img], function (event, cb) {
        gulp.start('image:build');
    });
});

gulp.task('serve', ['build'], function () {
    browserSync.init({
        server: {
            baseDir: "dist/",
            index: "index.html"
        }
    });
});

gulp.task('start', ['serve', 'watch']);