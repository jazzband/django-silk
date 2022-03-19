let gulp = require('gulp'),
    sass = require('gulp-sass');


gulp.task('watch', function () {
    gulp.watch('scss/**/*.scss', gulp.series('sass'));
});

gulp.task('sass', function () {
    return gulp.src('scss/**/*.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(gulp.dest('silk/static/silk/css'));
});
