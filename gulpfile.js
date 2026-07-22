let gulp = require('gulp'),
    sass = require('gulp-sass')(require('sass'));


gulp.task('watch', function () {
    gulp.watch('scss/**/*.scss', gulp.series('sass'));
});

gulp.task('sass', function () {
    return gulp.src('scss/**/*.scss')
        .pipe(sass.sync().on('error', sass.logError))
        .pipe(gulp.dest('silk/static/silk/css'));
});
