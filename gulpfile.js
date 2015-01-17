/**
 * Used for automating various tasks around testing & compilation.
 */
(function () {
    "use strict";

    var gulp = require('gulp'),
        shell = require('gulp-shell');

    var PYTHON_FILES = [
        'silk/**/*.py',
        'tests/tests/**/*.py',
        'tests/*.py'
    ];

    gulp.task('watch', function () {
        gulp.watch(PYTHON_FILES, ['test-python']);
    });

    gulp.task('test-python', shell.task(['./tests/manage.py test']));

})();

