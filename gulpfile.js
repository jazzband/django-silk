var gulp = require('gulp'),
    async = require('async'),
    _ = require('underscore'),
    plugins = require('gulp-load-plugins')();


var webpack = {
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
  gulp.watch('scss/**/*.scss', ['scss']);
});

gulp.task('scss', function () {
  gulp.src('scss/**/*.scss')
      .pipe(plugins.scss())
      .pipe(gulp.dest('silk/static/silk/css'))
});

var apps = {
  summary: 'js/summary/index.js'
};

gulp.task('js', function (done) {
  var appNames = Object.keys(apps),
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

