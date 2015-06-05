/**
 * Used for automating various tasks around testing & compilation.
 */
(function () {
    "use strict";

    var gulp = require('gulp'),
        plugins = require('gulp-load-plugins')();


    gulp.task('watch', function () {
        gulp.watch('scss/**/*.scss', ['scss']);
    });

    gulp.task('scss', function () {
        gulp.src('scss/**/*.scss')
            .pipe(plugins.scss())
            .pipe(gulp.dest('silk/static/silk/css'))
    });

})();