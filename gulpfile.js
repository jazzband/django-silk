let gulp = require('gulp'),
    async = require('async'),
    _ = require('underscore'),
    plugins = require('gulp-load-plugins')(),
    sass = require('gulp-sass');


let webpack = {
    externals: {
        'react': 'React',
        'jQuery': '$',
        'underscore': '_',
        'moment': 'moment',
        'async': 'async'
    },
    devtool: 'inline-source-map',
    module: {
        loaders: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                loader: 'babel-loader'
            }
        ]
    }
};


gulp.task('watch', function () {
    gulp.watch('scss/**/*.scss', gulp.series('sass'));
});

gulp.task('sass', function () {
    return gulp.src('scss/**/*.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(gulp.dest('silk/static/silk/css'));
});

let apps = {
    summary: 'js/summary/index.js'
};

gulp.task('js', function (done) {
    let appNames = Object.keys(apps),
        tasks = _.map(appNames, function (appName) {
            return function (done) {
                var path = apps[appName],
                    config = _.extend({}, webpack);
                gulp.src(path)
                    .pipe(plugins.webpack(config))
                    .pipe(plugins.rename(appName + '.js'))
                    .pipe(gulp.dest('silk/static/silk/js'))
                    .on('end', done);
            }
        });
    async.parallel(tasks, done);
});

