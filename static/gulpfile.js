'use strict';

var gulp = require('gulp'),
    watch = require('gulp-watch'),
    prefixer = require('gulp-autoprefixer'),
    cssmin = require('gulp-cssmin'),
    rename = require('gulp-rename'),
    browserSync = require('browser-sync').create();

var path = {
    source: {
        html: '*.html',
        html_partials: 'html_partials/*.html',
        js: 'js/**/*.js',
        css: 'css/*.css'
    },
    watch: {
        html: '*.html',
        html_partials: 'html_partials/*.html',
        js: 'js/**/*.js',
        css: 'css/*.css'
    }
};

gulp.task('html:build', function () {
    gulp.src(path.source.html)
        .pipe(browserSync.reload({stream: true}));
});

gulp.task('html_partials:build', function () {
    gulp.src(path.source.html_partials)
        .pipe(browserSync.reload({stream: true}));
});

gulp.task('css:build', function () {
    gulp.src(path.source.css)
        // .pipe(gulp.dest(path.source.css))
        // .pipe(cssmin())
        // .pipe(rename({suffix: '.min'}))
        .pipe(browserSync.reload({stream: true}));
});

gulp.task('js:build', function () {
    gulp.src(path.source.js)
        .pipe(browserSync.reload({stream: true}));
});

gulp.task('build', [
    'js:build',
    'css:build',
    'html:build',
    'html_partials:build'
]);

gulp.task('watch', function () {
    watch([path.watch.html], function (event, cb) {
        gulp.start('html:build');
    });
    watch([path.watch.css], function (event, cb) {
        gulp.start('css:build');
    });
    watch([path.watch.html_partials], function (event, cb) {
        gulp.start('html_partials:build');
    });
    watch([path.watch.js], function (event, cb) {
        gulp.start('js:build');
    });
});

gulp.task('serve', ['build'], function () {
    browserSync.init({
        server: {
            // baseDir: "/",
        }
    });
});

gulp.task('default', ['build', 'watch']);

gulp.task('start', ['serve', 'watch']);