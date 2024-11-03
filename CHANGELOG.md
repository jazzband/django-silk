# Change Log
## Unreleased

## [5.3.0](https://github.com/jazzband/django-silk/tree/5.3.0) (2024-10-25)
:release-by: Albert Wang (@albertyw)
[Full Changelog](https://github.com/jazzband/django-silk/compare/5.2.0..5.3.0)

**Note: this release removes support for Django 3.2 and Python 3.8**

**Features/Enhancements:**

 - Support python 3.13 (#747)

**Fixes:**

 - Upgrade jQuery-UI to 1.13.2 to fix XSS vulnerabity (#742)

**Maintenance and Cleanup:**

 - Remove Django 3.2 support (#736)
 - Drop support for python 3.8 (#749)
 - Update python dependencies (#748)


## [5.2.0](https://github.com/jazzband/django-silk/tree/5.2.0) (2024-08-17)
:release-by: Albert Wang (@albertyw)
[Full Changelog](https://github.com/jazzband/django-silk/compare/5.1.0..5.2.0)

**Features/Enhancements:**

 - Support Django 5.1 (#734, #732) @albertyw

**Fixes:**

 - Fix when Session, Authentication or Message middleware are not present (#667) @mgaligniana
 - Update 'tables_involved' property to include tables from UPDATE operation (#717) @emregeldegul
 - Fix double-escaping of the curl and Python example code (#709) @SpecLad
 - Correct units in profiling and requests pages (#725) @ka28kumar

**Maintenance and Cleanup:**

 - Update python dependencies (#733) @albertyw
 - Refactor SQL query time calculation to use Django aggregation (#720) @beltagymohamed
 - Fix test failures on Windows (#707) @SpecLad
 - Update workflow actions (#700) @albertyw
 - Update test matrix to latest version of django, postgres, and mariadb #701) @albertyw


## [5.1.0](https://github.com/jazzband/django-silk/tree/5.1.0) (2023-12-30)
:release-by: Albert Wang (@albertyw)
[Full Changelog](https://github.com/jazzband/django-silk/compare/5.0.4..5.1.0)

**Upgrading:**

This release includes [Fix deprecation warning for get_storage_class #669](https://github.com/jazzband/django-silk/pull/669)
which deprecates `SILKY_STORAGE_CLASS`.  Users should instead use the Django
`STORAGES` configuration.  See [README](https://github.com/albertyw/django-silk/blob/master/README.md#profiling)
and [Django documentation](https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-STORAGES)
for more information.

Also, for python 3.12, the `cProfile` stdlib library cannot be enabled multiple times concurrently.
Silk will therefore skip profiling if another profile is already enabled.


**Features/Enhancements:**

 - Allow option to delete profiles (#652) @viralj

**Fixes:**

 - Gracefully error out when there are concurrent profilers (#692) @albertyw
 - Always disable cProfile as part of cleanup (#699) @albertyw
 - Fix when Session, Authentication or Message middlewares are not present (#667) @mgaligniana

**Maintenance and Cleanup:**

 - Fix deprecation warning for get_storage_class (#669) @albertyw
 - Support Django 4.2 (#685) @albertyw
 - Support python 3.12 (#683) @albertyw
 - Support Django 5 (#686) @albertyw
 - Remove deprecated datetime.timezone.utc (#687) @albertyw
 - Derive version from importlib (#697) @robinchow

**Dependencies:**

 - Update python dependencies (#693) @albertyw


## [5.0.4](https://github.com/jazzband/django-silk/tree/5.0.4) (2023-09-17)
:release-by: Albert Wang (@albertyw)
[Full Changelog](https://github.com/jazzband/django-silk/compare/5.0.3..5.0.4)

**Features/Enhancements:**

 - Handle case-insensitive sensitive headers (#674) @shtimn
 - Add a "pagetitle" block to Silky templates (#661) @vsajip
 - Allow to generate more informative profile file name (#638) @k4rl85

**Maintenance and Cleanup:**

 - Remove unsupported versions of Django and Python (#668) @albertyw
 - Outsource all inline scripts and styles (#635) @sgelis
 - Remove support for looking up headers on django &lt;3.2 (#643) @albertyw

**Dependencies:**

 - Update python dependencies (#677) @albertyw


## [5.0.3](https://github.com/jazzband/django-silk/tree/5.0.3) (2023-01-12)
:release-by: Albert Wang (@albertyw)
[Full Changelog](https://github.com/jazzband/django-silk/compare/5.0.2..5.0.3)

**Fixes:**

 - #46 Retain ordering, view style and limit (#614)
 - #157 prevent encoding errors in params (#617)
 - #594 Silk fails on constraint check queries (#618) (Fixes compatibility with Django 4.1)

**Features/Enhancements:**

 - #132 Add action on sql query list (#611)
 - traceback only when needed (#387)

**Dependencies:**

 - #625 Drop dependency to jinja2


## [5.0.2](https://github.com/jazzband/django-silk/tree/5.0.2) (2022-10-12)
:release-by: Albert Wang (@albertyw)
[Full Changelog](https://github.com/jazzband/django-silk/compare/5.0.1...5.0.2)

**Fixes:**

 - Multipart forms and RawPostDataException (#592)
 - Decrease unnecessary database hits (#587) (#588)

**Features/Enhancements:**

 - Remove unneeded pytz package (#603)
 - Use contextlib in test_profile_parser (#590)
 - Add support for storages, that don't implement full filesystem path (#596)


## [5.0.1](https://github.com/jazzband/django-silk/tree/5.0.1) (2022-07-03)
:release-by: Albert Wang (@albertyw)
[Full Changelog](https://github.com/jazzband/django-silk/compare/5.0.0...5.0.1)

**Fixes:**

 - Add jquery UI 1.13.1 images and fix collectstatic (#576)


## [5.0.0](https://github.com/jazzband/django-silk/tree/5.0.0) (2022-06-20)
:release-by: Albert Wang (@albertyw)
[Full Changelog](https://github.com/jazzband/django-silk/compare/4.4.0...5.0.0)

**Features/Enhancements:**

- Drop support for Django 2.2 (EOL) (#567)
- Added silk_request_garbage_collect command for out-of-band garbage collection. (#541)


## [4.4.1](https://github.com/jazzband/django-silk/tree/4.4.1) (2022-07-03)
:release-by: Albert Wang (@albertyw)
[Full Changelog](https://github.com/jazzband/django-silk/compare/4.4.0...4.4.1)

**Fixes:**

 - Add jquery UI 1.13.1 images and fix collectstatic (#576)


## [4.4.0](https://github.com/jazzband/django-silk/tree/4.4.0) (2022-06-20)
:release-by: Albert Wang (@albertyw)
[Full Changelog](https://github.com/jazzband/django-silk/compare/4.3.0...4.4.0)

**Features/Enhancements:**

- Switch 'Apply' and 'Clear all filters' ordering
- Make filters on Requests tab more visible
- Add small margin for filter selects
- Add 'Clear all filters' button
- Add message when there are no requests to display
- Making the error logging more accurate and explicit
- Fixing #530 - Adding support for SILKY_EXPLAIN_FLAGS

**Maintenance and Cleanup:**

- Remove unused js compilation pipeline (#561)
- Fix pre-commit-config

**Dependencies:**

- Update jquery to 3.6.0 and jquery-ui to 1.13.1 [#508]
- [pre-commit.ci] pre-commit autoupdate (#560, #571)
- Add django-upgrade to pre-commit hooks (#566)

**Moved to 5.0.0**

- Drop support for Django 2.2 (EOL) (#567)


## [4.3.0](https://github.com/jazzband/django-silk/tree/4.3.0) (2022-03-01)
:release-by: Albert Wang (@albertyw)
[Full Changelog](https://github.com/jazzband/django-silk/compare/4.2.0...4.3.0)

**Fixes:**

- Use correct db in a multi db setup (https://github.com/jazzband/django-silk/issues/522)

**Dependencies:**

- Drop support for Python 3.6
- Add Python 3.10 compatibility
- Add Django 4.0 to tox.ini
- Update django version (#544)
- Django main (#528)
- Remove unneeded dependency Pygments

**Maintenance and Cleanup:**

- Jazzband: Created local 'CODE_OF_CONDUCT.md' from remote 'CODE_OF_CONDUCT.md'
- fix installation instructions in README
- Replace assertDictContainsSubset (#536)
- Fix issue avoid-misusing-assert-true found at https://codereview.doctor (#550)
- pre-commit autoupdate

## [4.2.0](https://github.com/jazzband/django-silk/tree/4.2.0) (2021-23-10)
:release-by: Asif Saif Uddin (@auvipy)
[Full Changelog](https://github.com/jazzband/django-silk/compare/4.1.0...4.2.0)
- #427 Passed wsgi request to SILKY_PYTHON_PROFILER_FUNC
- Added Django 3.1 & 3.2 to test matrix
- Replace url with re_path for Django 4.0
- Move CI to GitHub Actions. [\#460](https://github.com/jazzband/django-silk/pull/432) ([jezdez](https://github.com/jezdez))
- Do not crash when silk app is not included in urls
- Add the SILKY_JSON_ENSURE_ASCII configuration item to support Chinese
- Add row view for requests page (#440)
- RequestModelFactory: fallback if request body too large, fix #162 (#451)
- Add query execution plan to sql_detail (#452)
- Add Python 3.9 compatibility (#404)
- Replace re_path with path
- Fix transaction error for mysql
- parse query when count joins to match only Keyword
- fix: DB connection to ClearDB when multiple databases
- fix: DataCollector sql_queries model not found on filter(request=self.request)
- Generate missing row.css from sass
- Filter null values from most time overall summary
- Ensure sorting between longest requests
- Filter null values from most db time summary
- Ensure sorting between most db time requests
- Temporary fix for testing Django 2.2
- Fix egg metadata error
- Fixed a bug that the profile tab could not be opened when the source code contains japanese
- fix incorrectly made decorator
- Ensure sorting between most db queries requests
- Add tests that access the actual DB (#493)
- remove python 2 style codes from across the codebase
- Fix broken test on Windows 10 (SQLite) (#504)
- Remove Make Migrations (#503)
- Add Python 3.10 compatibility (#527)


## [4.1.0](https://github.com/jazzband/django-silk/tree/4.1.0) (2020-08-07)

[Full Changelog](https://github.com/jazzband/django-silk/compare/4.0.1...4.1.0)


**New features/Implemented enhancements:**

- Make compatible with Django 3.1 [\#432](https://github.com/jazzband/django-silk/pull/432) ([Tirzono](https://github.com/Tirzono))


**Fixed bugs:**

- Capture entire key name during cleansing in \_mask\_credentials [\#414](https://github.com/jazzband/django-silk/pull/414) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- Clear DB error when configuring silk to use a non-' default' database [\#417](https://github.com/jazzband/django-silk/pull/417) ([eshxcmhk](https://github.com/eshxcmhk))
- Fix force\_text RemovedInDjango40Warning [\#422](https://github.com/jazzband/django-silk/pull/422) ([justinmayhew](https://github.com/justinmayhew))


**Closed issues:**

- \_mask\_credentials uses UGC in a regex substitution [\#410](https://github.com/jazzband/django-silk/issues/410) ([barm](https://github.com/barm))
- Django Silk is not compatible with Django 3.1: EmptyResultSet is removed in Django 3.1 [\#431](https://github.com/jazzband/django-silk/issues/431) ([Tirzono](https://github.com/Tirzono))


**Merged pull requests:**

- Wrap re.sub() in try-except [\#412](https://github.com/jazzband/django-silk/pull/412) ([bambookchos](https://github.com/bambookchos))
- Replace the call to re.findall with re.sub in \_mask\_credentials so matched values are not treated as regex patterns [\#413](https://github.com/jazzband/django-silk/pull/413) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- Capture entire key name during cleansing in \_mask\_credentials [\#414](https://github.com/jazzband/django-silk/pull/414) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- Clear DB error when configuring silk to use a non-' default' database [\#417](https://github.com/jazzband/django-silk/pull/417) ([eshxcmhk](https://github.com/eshxcmhk))
- Fix force\_text RemovedInDjango40Warning [\#422](https://github.com/jazzband/django-silk/pull/422) ([justinmayhew](https://github.com/justinmayhew))
- Make compatible with Django 3.1 [\#432](https://github.com/jazzband/django-silk/pull/432) ([Tirzono](https://github.com/Tirzono))
- Update README.md django-silk is tested with Django 3.1 [\#433](https://github.com/jazzband/django-silk/pull/433) ([Tirzono](https://github.com/Tirzono))


## [4.0.1](https://github.com/jazzband/django-silk/tree/4.0.1) (2020-03-12)

[Full Changelog](https://github.com/jazzband/django-silk/compare/4.0.0...4.0.1)


**New features/Implemented enhancements:**

- Restructured clear db HTML [\#399](https://github.com/jazzband/django-silk/pull/399) ([nasirhjafri](https://github.com/nasirhjafri))
- JS workflow cleanup [\#397](https://github.com/jazzband/django-silk/pull/397) ([nasirhjafri](https://github.com/nasirhjafri))
- Refactor QA setup [\#393](https://github.com/jazzband/django-silk/pull/393) ([aleksihakli](https://github.com/aleksihakli))


**Fixed bugs:**

- docs: Fix simple typo, tracebackk -> traceback [\#406](https://github.com/jazzband/django-silk/pull/406) ([timgates42](https://github.com/timgates42))
- Clear DB page doesn't work with PostgreSQL and SQLite [\#396](https://github.com/jazzband/django-silk/pull/396) ([nasirhjafri](https://github.com/nasirhjafri))


**Closed issues:**

- The "Clear DB" page doesn't work with PostgreSQL [\#395](https://github.com/jazzband/django-silk/issues/395) ([Ikalou](https://github.com/Ikalou))


**Merged pull requests:**

- docs: Fix simple typo, tracebackk -> traceback [\#406](https://github.com/jazzband/django-silk/pull/406) ([timgates42](https://github.com/timgates42))
- Restructured clear db HTML [\#399](https://github.com/jazzband/django-silk/pull/399) ([nasirhjafri](https://github.com/nasirhjafri))
- JS workflow cleanup [\#397](https://github.com/jazzband/django-silk/pull/397) ([nasirhjafri](https://github.com/nasirhjafri))
- Clear DB page doesn't work with PostgreSQL and SQLite [\#396](https://github.com/jazzband/django-silk/pull/396) ([nasirhjafri](https://github.com/nasirhjafri))
- Refactor QA setup [\#393](https://github.com/jazzband/django-silk/pull/393) ([aleksihakli](https://github.com/aleksihakli))


## [4.0.0](https://github.com/jazzband/django-silk/tree/4.0.0) (2020-01-09)

[Full Changelog](https://github.com/jazzband/django-silk/compare/3.0.4...4.0.0)

**New features/Implemented enhancements:**

- Ability to clean up all requests/queries [\#368](https://github.com/jazzband/django-silk/pull/368) ([nasirhjafri](https://github.com/nasirhjafri))
- Used bulk_create to save number of queries [\#370](https://github.com/jazzband/django-silk/pull/370) ([nasirhjafri](https://github.com/nasirhjafri))
- Dropped Python 2 and 3.4 support [\#380](https://github.com/jazzband/django-silk/pull/380) ([munza](https://github.com/munza))
- Added Python 3.8 support [\#380](https://github.com/jazzband/django-silk/pull/380) ([nasirhjafri](https://github.com/nasirhjafri))
- Removed django<2.2 support and added django 3.0 support [\#385](https://github.com/jazzband/django-silk/pull/385) ([nasirhjafri](https://github.com/nasirhjafri))
- Add function support for enabling profiling [\#391](https://github.com/jazzband/django-silk/pull/391) ([tredzko](https://github.com/tredzko))

**Fixed bugs:**

- Mask authorization header [\#376](https://github.com/jazzband/django-silk/pull/376) ([StefanMich](https://github.com/StefanMich))

**Closed issues:**

- Ability to clean up all requests/queries [\#365](https://github.com/jazzband/django-silk/issues/365)
- Use bulk_create to save number of queries [\#369](https://github.com/jazzband/django-silk/issues/369)
- Headers are not sanitized [\#375](https://github.com/jazzband/django-silk/issues/375)
- Django 3 support [\#382](https://github.com/jazzband/django-silk/issues/382)
- Support functional cProfile enable [\#390](https://github.com/jazzband/django-silk/issues/390)


**Merged pull requests:**

- Mask authorization header [\#376](https://github.com/jazzband/django-silk/pull/376) ([StefanMich](https://github.com/StefanMich))
- Ability to clean up all requests/queries [\#368](https://github.com/jazzband/django-silk/pull/368) ([nasirhjafri](https://github.com/nasirhjafri))
- Used bulk_create to save number of queries [\#370](https://github.com/jazzband/django-silk/pull/370) ([nasirhjafri](https://github.com/nasirhjafri))
- Dropped Python 2 and 3.4 support [\#380](https://github.com/jazzband/django-silk/pull/380) ([munza](https://github.com/munza))
- Added Python 3.8 support [\#380](https://github.com/jazzband/django-silk/pull/380) ([nasirhjafri](https://github.com/nasirhjafri))
- Removed django<2.2 support and added django 3.0 support [\#385](https://github.com/jazzband/django-silk/pull/385) ([nasirhjafri](https://github.com/nasirhjafri))
- Add function support for enabling profiling [\#391](https://github.com/jazzband/django-silk/pull/391) ([tredzko](https://github.com/tredzko))


## [3.0.4](https://github.com/jazzband/django-silk/tree/3.0.4) (2019-08-12)

[Full Changelog](https://github.com/jazzband/django-silk/compare/3.0.2...3.0.4)

**Implemented enhancements:**

- templates: limit select width to its container one [\#351](https://github.com/jazzband/django-silk/pull/351) ([xrmx](https://github.com/xrmx))
- Clean up RemovedInDjango30Warning with {% load staticfiles %} [\#353](https://github.com/jazzband/django-silk/pull/353) ([devmonkey22](https://github.com/devmonkey22))
- Simplify pattern masking and handle dicts [\#355](https://github.com/jazzband/django-silk/pull/355) ([Chris7](https://github.com/Chris7))

**Fixed bugs:**

- Fix masking sensitive data in batch JSON request [\#342](https://github.com/jazzband/django-silk/pull/342) ([nikolaik](https://github.com/nikolaik))
- Fix project url on PyPi [\#343](https://github.com/jazzband/django-silk/pull/343) ([luzfcb](https://github.com/luzfcb))

**Closed issues:**

- Clean up RemovedInDjango30Warning warning re `load staticfiles` in Django 2.1+ [\#352](https://github.com/jazzband/django-silk/issues/352)

**Merged pull requests:**

- Fix masking sensitive data in batch JSON request [\#342](https://github.com/jazzband/django-silk/pull/342) ([nikolaik](https://github.com/nikolaik))
- Fix project url on PyPi [\#343](https://github.com/jazzband/django-silk/pull/343) ([luzfcb](https://github.com/luzfcb))
- templates: limit select width to its container one [\#351](https://github.com/jazzband/django-silk/pull/351) ([xrmx](https://github.com/xrmx))
- Clean up RemovedInDjango30Warning with {% load staticfiles %} [\#353](https://github.com/jazzband/django-silk/pull/353) ([devmonkey22](https://github.com/devmonkey22))
- Simplify pattern masking and handle dicts [\#355](https://github.com/jazzband/django-silk/pull/355) ([Chris7](https://github.com/Chris7))


## [3.0.2](https://github.com/jazzband/django-silk/tree/3.0.2) (2019-04-23)

[Full Changelog](https://github.com/jazzband/django-silk/compare/3.0.1...3.0.2)

**Implemented enhancements:**

- Add testing support for django 2.2 [\#340](https://github.com/jazzband/django-silk/pull/340) ([mbeacom](https://github.com/mbeacom))
- SILKY\_MIDDLEWARE\_CLASS option [\#334](https://github.com/jazzband/django-silk/pull/334) ([vartagg](https://github.com/vartagg))

**Fixed bugs:**

- Long url path causes Http 500 [\#312](https://github.com/jazzband/django-silk/issues/312)

**Closed issues:**

- Permission checking is skipped due to order of silk\_profile decorator [\#336](https://github.com/jazzband/django-silk/issues/336)
- Support gprof2dot 2017.09.19 [\#332](https://github.com/jazzband/django-silk/issues/332)
- Duplicate \#310 [\#328](https://github.com/jazzband/django-silk/issues/328)
- Profiling management commands [\#327](https://github.com/jazzband/django-silk/issues/327)
- NoReverseMatch at /cart/detail/ Reverse for 'cart\_add' with arguments not found. [\#324](https://github.com/jazzband/django-silk/issues/324)
- Request body sanitization [\#305](https://github.com/jazzband/django-silk/issues/305)
- How to profile middleware? [\#303](https://github.com/jazzband/django-silk/issues/303)
- Disabling Silk for specific URLs [\#292](https://github.com/jazzband/django-silk/issues/292)
- silk\_clear\_request\_log fails on Postgres [\#290](https://github.com/jazzband/django-silk/issues/290)
- silk profile is not work, with dango-version 2.0.2 and django-silk version 2.0.0 [\#277](https://github.com/jazzband/django-silk/issues/277)
- DataError: value too long for type character varying\(190\) [\#179](https://github.com/jazzband/django-silk/issues/179)

**Merged pull requests:**

- Update gprof2dot requirement [\#333](https://github.com/jazzband/django-silk/pull/333) ([Regzon](https://github.com/Regzon))
- Make Request.garbage\_collect cheaper [\#331](https://github.com/jazzband/django-silk/pull/331) ([xrmx](https://github.com/xrmx))
- Sort view filters values [\#330](https://github.com/jazzband/django-silk/pull/330) ([xrmx](https://github.com/xrmx))
- Update Travis CI matrix [\#326](https://github.com/jazzband/django-silk/pull/326) ([kevin-brown](https://github.com/kevin-brown))
- Fix unit for max response body size in readme [\#325](https://github.com/jazzband/django-silk/pull/325) ([st4lk](https://github.com/st4lk))
- Mask sensitive data [\#322](https://github.com/jazzband/django-silk/pull/322) ([egichuri](https://github.com/egichuri))
- Disclose security issues [\#321](https://github.com/jazzband/django-silk/pull/321) ([acu192](https://github.com/acu192))
- If there is no DataCollector\(\).request then don't wrap sql queries [\#320](https://github.com/jazzband/django-silk/pull/320) ([rwlogel](https://github.com/rwlogel))
- Prevent path or view\_name being longer than 190 characters [\#314](https://github.com/jazzband/django-silk/pull/314) ([smaccona](https://github.com/smaccona))
- Disable postgres USER triggers [\#299](https://github.com/jazzband/django-silk/pull/299) ([gforcada](https://github.com/gforcada))
- Fix \#297 remove explicit byte string from migration 0003 [\#298](https://github.com/jazzband/django-silk/pull/298) ([florianm](https://github.com/florianm))
- Modernize middleware [\#296](https://github.com/jazzband/django-silk/pull/296) ([gforcada](https://github.com/gforcada))
- Added a simple view in request detail context allowing to get python profile [\#295](https://github.com/jazzband/django-silk/pull/295) ([laurentb2](https://github.com/laurentb2))

## [3.0.1](https://github.com/jazzband/django-silk/tree/3.0.1) (2018-07-03)
[Full Changelog](https://github.com/jazzband/django-silk/compare/3.0.0...3.0.1)

**Closed issues:**

- ProgrammingError raised from silk\_clear\_request\_log [\#293](https://github.com/jazzband/django-silk/issues/293)
- Make a new release of django-silk [\#282](https://github.com/jazzband/django-silk/issues/282)

**Merged pull requests:**

- \#290 Fix silk\_clear\_request\_log errors on Postgres [\#291](https://github.com/jazzband/django-silk/pull/291) ([devmonkey22](https://github.com/devmonkey22))

## [3.0.0](https://github.com/jazzband/django-silk/tree/3.0.0) (2018-05-15)
[Full Changelog](https://github.com/jazzband/django-silk/compare/2.0.0...3.0.0)

**Implemented enhancements:**

- Limiting request/response data don't available in pypi version  [\#218](https://github.com/jazzband/django-silk/issues/218)

**Fixed bugs:**

- silk\_clear\_request\_log taking longer than 30 minutes [\#239](https://github.com/jazzband/django-silk/issues/239)

**Closed issues:**

- Meta profiling does not work with Django 2.0 and higher [\#274](https://github.com/jazzband/django-silk/issues/274)
- Force opening a new window for SQL queries is very annoying [\#271](https://github.com/jazzband/django-silk/issues/271)
- DB Deadlock when stress testing with silk [\#265](https://github.com/jazzband/django-silk/issues/265)
- proplem with propagating code to pypi  [\#264](https://github.com/jazzband/django-silk/issues/264)
- PSA: Cleanup silk\_requests before updating to 1.1.0 [\#261](https://github.com/jazzband/django-silk/issues/261)
- Release 2.0.0 [\#259](https://github.com/jazzband/django-silk/issues/259)

**Merged pull requests:**

- Remove gitter links [\#285](https://github.com/jazzband/django-silk/pull/285) ([albertyw](https://github.com/albertyw))
- Release 3.0.0 [\#283](https://github.com/jazzband/django-silk/pull/283) ([albertyw](https://github.com/albertyw))
- Fix garbage collection logic for small tables [\#280](https://github.com/jazzband/django-silk/pull/280) ([albertyw](https://github.com/albertyw))
- Fix view name [\#278](https://github.com/jazzband/django-silk/pull/278) ([drppi44](https://github.com/drppi44))
- Revert "Opening sql queries in new tab is very useful" [\#276](https://github.com/jazzband/django-silk/pull/276) ([albertyw](https://github.com/albertyw))
- Fix issue \#274 [\#275](https://github.com/jazzband/django-silk/pull/275) ([MKolman](https://github.com/MKolman))
- Truncate tables when running silk\_clear\_request\_log [\#270](https://github.com/jazzband/django-silk/pull/270) ([albertyw](https://github.com/albertyw))
- Makes example\_app.models.Product.photo.upload\_to a string instead of bytes [\#268](https://github.com/jazzband/django-silk/pull/268) ([vbawa](https://github.com/vbawa))
- Make garbage collection filter more efficient [\#267](https://github.com/jazzband/django-silk/pull/267) ([albertyw](https://github.com/albertyw))
-  Drop support for Django \< 1.11 and remove workarounds [\#266](https://github.com/jazzband/django-silk/pull/266) ([jdufresne](https://github.com/jdufresne))

## [2.0.0](https://github.com/jazzband/django-silk/tree/2.0.0) (2018-01-16)
[Full Changelog](https://github.com/jazzband/django-silk/compare/1.1.0...2.0.0)

**Fixed bugs:**

- Links for Readme.md not working. [\#250](https://github.com/jazzband/django-silk/issues/250)

**Closed issues:**

- pypi version [\#252](https://github.com/jazzband/django-silk/issues/252)
- Remove support for django 1.7 [\#247](https://github.com/jazzband/django-silk/issues/247)
- migrations/0005\_increase\_request\_prof\_file\_length.py does not match code [\#244](https://github.com/jazzband/django-silk/issues/244)
- Excessive number of queries in class method profile [\#240](https://github.com/jazzband/django-silk/issues/240)
- Django 2.0 support [\#229](https://github.com/jazzband/django-silk/issues/229)
- Create new release of silk [\#187](https://github.com/jazzband/django-silk/issues/187)

**Merged pull requests:**

- Release 2.0.0 [\#260](https://github.com/jazzband/django-silk/pull/260) ([albertyw](https://github.com/albertyw))
- function declaration fix [\#254](https://github.com/jazzband/django-silk/pull/254) ([Yolley](https://github.com/Yolley))
- Opening sql queries in new tab is very useful [\#253](https://github.com/jazzband/django-silk/pull/253) ([lokeshatbigbasket](https://github.com/lokeshatbigbasket))
- Use force\_text in ResponseModelFactory to avoid b' prefix in django 2 [\#251](https://github.com/jazzband/django-silk/pull/251) ([aadu](https://github.com/aadu))
- Remove django support 1.7 [\#249](https://github.com/jazzband/django-silk/pull/249) ([albertyw](https://github.com/albertyw))
- Remove django 1.6 references [\#248](https://github.com/jazzband/django-silk/pull/248) ([albertyw](https://github.com/albertyw))
- Update development status and python support to package classifiers [\#246](https://github.com/jazzband/django-silk/pull/246) ([albertyw](https://github.com/albertyw))
- fix migration for request.prof\_file field [\#245](https://github.com/jazzband/django-silk/pull/245) ([dennybiasiolli](https://github.com/dennybiasiolli))
- fix alternative github tags installation url [\#243](https://github.com/jazzband/django-silk/pull/243) ([dennybiasiolli](https://github.com/dennybiasiolli))

## [1.1.0](https://github.com/jazzband/django-silk/tree/1.1.0) (2017-12-27)
[Full Changelog](https://github.com/jazzband/django-silk/compare/1.0.0...1.1.0)

**Implemented enhancements:**

- RemovedInDjango20Warning: on\_delete will be a required arg for OneToOneField in Django 2.0. [\#183](https://github.com/jazzband/django-silk/issues/183)
- README missing info about how to import decorator [\#180](https://github.com/jazzband/django-silk/issues/180)
- Use redis for backend [\#163](https://github.com/jazzband/django-silk/issues/163)
- Difficult to install on windows: Needs wheels. [\#149](https://github.com/jazzband/django-silk/issues/149)
- Organise cProfile output as a sortable, more organised table. [\#33](https://github.com/jazzband/django-silk/issues/33)

**Closed issues:**

- Silk is incompatible with django-fullclean [\#219](https://github.com/jazzband/django-silk/issues/219)
- The dashboard shows views with no queries as most time taken in database [\#217](https://github.com/jazzband/django-silk/issues/217)
- No end\_time for any captured request [\#213](https://github.com/jazzband/django-silk/issues/213)
- Bad alignment in profile table [\#206](https://github.com/jazzband/django-silk/issues/206)
- Visualization not visible [\#205](https://github.com/jazzband/django-silk/issues/205)
- Storage class as a setting [\#202](https://github.com/jazzband/django-silk/issues/202)
- Consider moving project to jazzband [\#184](https://github.com/jazzband/django-silk/issues/184)
- Request detail page never loads [\#175](https://github.com/jazzband/django-silk/issues/175)
- Number of queries and time showing as 0 [\#174](https://github.com/jazzband/django-silk/issues/174)
- NameError: name 'silk\_profile' is not defined [\#172](https://github.com/jazzband/django-silk/issues/172)
- Query time-outs [\#158](https://github.com/jazzband/django-silk/issues/158)

**Merged pull requests:**

- Release 1.1.0 [\#242](https://github.com/jazzband/django-silk/pull/242) ([albertyw](https://github.com/albertyw))
- Update package versions for test project [\#241](https://github.com/jazzband/django-silk/pull/241) ([albertyw](https://github.com/albertyw))
- Return immediately [\#235](https://github.com/jazzband/django-silk/pull/235) ([Stranger6667](https://github.com/Stranger6667))
- Fix missing db\_time field [\#234](https://github.com/jazzband/django-silk/pull/234) ([albertyw](https://github.com/albertyw))
- Test django 2 in travis [\#233](https://github.com/jazzband/django-silk/pull/233) ([albertyw](https://github.com/albertyw))
- Lint silk directory and fix a python 3 blocker [\#232](https://github.com/jazzband/django-silk/pull/232) ([albertyw](https://github.com/albertyw))
- Fix flaky test by rounding off floats [\#231](https://github.com/jazzband/django-silk/pull/231) ([albertyw](https://github.com/albertyw))
- Fix github silk links to point to jazzband [\#230](https://github.com/jazzband/django-silk/pull/230) ([albertyw](https://github.com/albertyw))
- Update docs to clarify how to install the middleware [\#228](https://github.com/jazzband/django-silk/pull/228) ([albertyw](https://github.com/albertyw))
- Fix Django 2 deprecations [\#227](https://github.com/jazzband/django-silk/pull/227) ([albertyw](https://github.com/albertyw))
- Add extra documentation covering environment variables and running tests [\#226](https://github.com/jazzband/django-silk/pull/226) ([richardnias](https://github.com/richardnias))
- Filter out views that took no time in the database for the most time … [\#225](https://github.com/jazzband/django-silk/pull/225) ([hvdklauw](https://github.com/hvdklauw))
- Removed typo errors and fixed contractions [\#222](https://github.com/jazzband/django-silk/pull/222) ([basifat](https://github.com/basifat))
- gprof2dot had a breaking change in 2017.09.19 [\#221](https://github.com/jazzband/django-silk/pull/221) ([richardnias](https://github.com/richardnias))
- Allow prof\_file to be blank, not null [\#220](https://github.com/jazzband/django-silk/pull/220) ([richardnias](https://github.com/richardnias))
- Changed the theme of gprof2dot output to be more inline with rest of silk design [\#210](https://github.com/jazzband/django-silk/pull/210) ([danielbradburn](https://github.com/danielbradburn))
- configurable storage class [\#204](https://github.com/jazzband/django-silk/pull/204) ([smcoll](https://github.com/smcoll))
- increase Request.prof\_file max\_length to 300 [\#203](https://github.com/jazzband/django-silk/pull/203) ([smcoll](https://github.com/smcoll))
- \#33 organise cprofile output as a sortable table [\#200](https://github.com/jazzband/django-silk/pull/200) ([danielbradburn](https://github.com/danielbradburn))
- left align pre tag text [\#199](https://github.com/jazzband/django-silk/pull/199) ([smcoll](https://github.com/smcoll))
- add .venv\* to .gitignore [\#198](https://github.com/jazzband/django-silk/pull/198) ([danielbradburn](https://github.com/danielbradburn))
- Add missing gprof2dot to setup.py [\#197](https://github.com/jazzband/django-silk/pull/197) ([danielbradburn](https://github.com/danielbradburn))
- README changes for visualisation and sql summary table sorting [\#195](https://github.com/jazzband/django-silk/pull/195) ([danielbradburn](https://github.com/danielbradburn))
- Added UI element to filter requests by http verb [\#194](https://github.com/jazzband/django-silk/pull/194) ([danielbradburn](https://github.com/danielbradburn))
- Sortable sql table [\#193](https://github.com/jazzband/django-silk/pull/193) ([danielbradburn](https://github.com/danielbradburn))
- Visualize profile result [\#192](https://github.com/jazzband/django-silk/pull/192) ([danielbradburn](https://github.com/danielbradburn))
- Added status code filter [\#191](https://github.com/jazzband/django-silk/pull/191) ([danielbradburn](https://github.com/danielbradburn))
- Set jazzband to limit the number of rows of request/response data [\#190](https://github.com/jazzband/django-silk/pull/190) ([albertyw](https://github.com/albertyw))
- Add python 3.6 to travis config [\#189](https://github.com/jazzband/django-silk/pull/189) ([albertyw](https://github.com/albertyw))
- Add explicit on\_delete to foreign key and one to one relationships [\#188](https://github.com/jazzband/django-silk/pull/188) ([albertyw](https://github.com/albertyw))
- Replace django-silk organization with jazzband [\#186](https://github.com/jazzband/django-silk/pull/186) ([albertyw](https://github.com/albertyw))
- Jazzband migration [\#185](https://github.com/jazzband/django-silk/pull/185) ([mtford90](https://github.com/mtford90))
- Deprecation: update to warning [\#177](https://github.com/jazzband/django-silk/pull/177) ([lammertw](https://github.com/lammertw))
- Add text-align property to pyprofile class for readability [\#176](https://github.com/jazzband/django-silk/pull/176) ([jeffreyckchau](https://github.com/jeffreyckchau))
- Mention collectstatic [\#173](https://github.com/jazzband/django-silk/pull/173) ([goetzk](https://github.com/goetzk))

## [1.0.0](https://github.com/jazzband/django-silk/tree/1.0.0) (2017-03-25)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.7.3...1.0.0)

**Fixed bugs:**

- Silk shows 0 time for all requests? [\#161](https://github.com/jazzband/django-silk/issues/161)
- Failed to install index for silk.Request model: \(1071, 'Specified key was too long; max key length is 767 bytes'\) [\#38](https://github.com/jazzband/django-silk/issues/38)
- IntegrityError: duplicate key value violates unique constraint "silk\_response\_request\_id\_key" [\#26](https://github.com/jazzband/django-silk/issues/26)

**Closed issues:**

- There is no reference to download a profile [\#170](https://github.com/jazzband/django-silk/issues/170)
- Build fails occasionally due to "missing manage.py" [\#32](https://github.com/jazzband/django-silk/issues/32)

**Merged pull requests:**

- Fixes \#170 [\#171](https://github.com/jazzband/django-silk/pull/171) ([perdy](https://github.com/perdy))
- Wheel support [\#168](https://github.com/jazzband/django-silk/pull/168) ([auvipy](https://github.com/auvipy))
- Improved MySQL support [\#167](https://github.com/jazzband/django-silk/pull/167) ([smaccona](https://github.com/smaccona))
- some style improvements [\#166](https://github.com/jazzband/django-silk/pull/166) ([auvipy](https://github.com/auvipy))
- Update travis matrix and requirments dependencies versions [\#165](https://github.com/jazzband/django-silk/pull/165) ([auvipy](https://github.com/auvipy))
- Fixes \#161 [\#164](https://github.com/jazzband/django-silk/pull/164) ([perdy](https://github.com/perdy))

## [0.7.3](https://github.com/jazzband/django-silk/tree/0.7.3) (2017-02-13)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.7.2...0.7.3)

**Fixed bugs:**

- Profiling files get copied into MEDIA\_ROOT [\#151](https://github.com/jazzband/django-silk/issues/151)
- Bad requirements for postgres based installations [\#142](https://github.com/jazzband/django-silk/issues/142)

**Closed issues:**

- Middleware setting in Django 1.10 [\#159](https://github.com/jazzband/django-silk/issues/159)
- When installing silk asking for mysql library. But I'm using postgresql. [\#150](https://github.com/jazzband/django-silk/issues/150)
- No Silk profiling was performed for this request. Use the silk\_profile decorator/context manager to do so. [\#147](https://github.com/jazzband/django-silk/issues/147)
- ProgrammingError on postgresql [\#146](https://github.com/jazzband/django-silk/issues/146)
- \[Error\]\[Bug\]adding silk middleware in MIDDLEWARE causes ImportError [\#108](https://github.com/jazzband/django-silk/issues/108)

**Merged pull requests:**

- Update middleware setting for Django \>= 1.10 [\#160](https://github.com/jazzband/django-silk/pull/160) ([ukjin1192](https://github.com/ukjin1192))
- Add favorite icons [\#156](https://github.com/jazzband/django-silk/pull/156) ([phuong](https://github.com/phuong))
- Bugfix for issue \#153 [\#155](https://github.com/jazzband/django-silk/pull/155) ([Drache91](https://github.com/Drache91))
- Improve profile storage [\#152](https://github.com/jazzband/django-silk/pull/152) ([r3m0t](https://github.com/r3m0t))

## [0.7.2](https://github.com/jazzband/django-silk/tree/0.7.2) (2016-12-03)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.7.1...0.7.2)

**Closed issues:**

- Pypi version upload [\#141](https://github.com/jazzband/django-silk/issues/141)

**Merged pull requests:**

- Allow using Django 1.10 MIDDLEWARE setting instead of MIDDLEWARE\_CLASSES [\#148](https://github.com/jazzband/django-silk/pull/148) ([lockie](https://github.com/lockie))
- Travis config to test on the different django database backends. [\#145](https://github.com/jazzband/django-silk/pull/145) ([mattjegan](https://github.com/mattjegan))
- Updates exception handling to use Django DatabaseError class [\#144](https://github.com/jazzband/django-silk/pull/144) ([hanleyhansen](https://github.com/hanleyhansen))
- Fix for byte string incompatibility in ResponseModelFactory.body\(\) on py3 [\#143](https://github.com/jazzband/django-silk/pull/143) ([aljp](https://github.com/aljp))

## [0.7.1](https://github.com/jazzband/django-silk/tree/0.7.1) (2016-10-01)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.7.0...0.7.1)

**Merged pull requests:**

- Operational Error When Silk Is Used On Big SQL Queries [\#140](https://github.com/jazzband/django-silk/pull/140) ([hanleyhansen](https://github.com/hanleyhansen))

## [0.7.0](https://github.com/jazzband/django-silk/tree/0.7.0) (2016-09-21)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.6.2...0.7.0)

**Implemented enhancements:**

- Select a path to save profiling files [\#131](https://github.com/jazzband/django-silk/issues/131)

**Merged pull requests:**

- Remove trailing slashes in MANIFEST.in [\#139](https://github.com/jazzband/django-silk/pull/139) ([leifdenby](https://github.com/leifdenby))
- Django 1.10 compatibility [\#138](https://github.com/jazzband/django-silk/pull/138) ([shanx](https://github.com/shanx))
- Swap imports to avoid emitting warnings [\#136](https://github.com/jazzband/django-silk/pull/136) ([blag](https://github.com/blag))
- Profiler files path configurable [\#135](https://github.com/jazzband/django-silk/pull/135) ([javaguirre](https://github.com/javaguirre))
- Fix ignored content body [\#134](https://github.com/jazzband/django-silk/pull/134) ([aehlke](https://github.com/aehlke))
- Namespaced loggers [\#133](https://github.com/jazzband/django-silk/pull/133) ([aehlke](https://github.com/aehlke))

## [0.6.2](https://github.com/jazzband/django-silk/tree/0.6.2) (2016-07-28)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.6.1...0.6.2)

**Closed issues:**

- SnakeViz integration [\#83](https://github.com/jazzband/django-silk/issues/83)

**Merged pull requests:**

- don't crash when a route is 404 [\#129](https://github.com/jazzband/django-silk/pull/129) ([chrono](https://github.com/chrono))

## [0.6.1](https://github.com/jazzband/django-silk/tree/0.6.1) (2016-07-13)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.6.0...0.6.1)

**Closed issues:**

- Latest version of django-silk not installing because of missing dependency [\#127](https://github.com/jazzband/django-silk/issues/127)
- README.md missing in v0.6 [\#125](https://github.com/jazzband/django-silk/issues/125)

**Merged pull requests:**

- use any readme [\#128](https://github.com/jazzband/django-silk/pull/128) ([SzySteve](https://github.com/SzySteve))

## [0.6.0](https://github.com/jazzband/django-silk/tree/0.6.0) (2016-07-12)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.5.7...0.6.0)

**Closed issues:**

- Local Dev of Silk. Template Error. [\#121](https://github.com/jazzband/django-silk/issues/121)
- Using django six rather then maintaining one [\#112](https://github.com/jazzband/django-silk/issues/112)
- PyPi release [\#106](https://github.com/jazzband/django-silk/issues/106)

**Merged pull requests:**

- update pillow requirement so installation succeeds [\#124](https://github.com/jazzband/django-silk/pull/124) ([SzySteve](https://github.com/SzySteve))
- Give users the ability to export .prof binary files for every request [\#123](https://github.com/jazzband/django-silk/pull/123) ([hanleyhansen](https://github.com/hanleyhansen))
- Make Silk Great Again and Upgrade Dev Project [\#122](https://github.com/jazzband/django-silk/pull/122) ([hanleyhansen](https://github.com/hanleyhansen))
- make file paths clickable that don't start with a slash [\#120](https://github.com/jazzband/django-silk/pull/120) ([chrono](https://github.com/chrono))
- clear data store in chunks [\#119](https://github.com/jazzband/django-silk/pull/119) ([chrono](https://github.com/chrono))
- remove claim to support django 1.6 [\#118](https://github.com/jazzband/django-silk/pull/118) ([chrono](https://github.com/chrono))
- removed six six utils and tests [\#117](https://github.com/jazzband/django-silk/pull/117) ([auvipy](https://github.com/auvipy))
- used django utils six instead of sils utls six in some module [\#116](https://github.com/jazzband/django-silk/pull/116) ([auvipy](https://github.com/auvipy))
- Lint fix and code cleaning [\#114](https://github.com/jazzband/django-silk/pull/114) ([auvipy](https://github.com/auvipy))
- small updates [\#113](https://github.com/jazzband/django-silk/pull/113) ([auvipy](https://github.com/auvipy))
- Render function instead of render\_to\_response [\#111](https://github.com/jazzband/django-silk/pull/111) ([auvipy](https://github.com/auvipy))
- remove south migrations as not needed in less then 1.7 [\#110](https://github.com/jazzband/django-silk/pull/110) ([auvipy](https://github.com/auvipy))
- versions upgrade and obsolete versions removal  [\#109](https://github.com/jazzband/django-silk/pull/109) ([auvipy](https://github.com/auvipy))
- Supporting django\<1.8 [\#107](https://github.com/jazzband/django-silk/pull/107) ([wm3ndez](https://github.com/wm3ndez))

## [0.5.7](https://github.com/jazzband/django-silk/tree/0.5.7) (2016-03-16)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.5.6...0.5.7)

**Implemented enhancements:**

- Unittesting [\#87](https://github.com/jazzband/django-silk/issues/87)
- Add Ascending/Descending sort order GET parameter in RequestsView [\#84](https://github.com/jazzband/django-silk/issues/84)
- Support binary response bodies [\#1](https://github.com/jazzband/django-silk/issues/1)

**Fixed bugs:**

- TemplateSyntaxError at /silk/ Invalid filter: 'silk\_date\_time' [\#82](https://github.com/jazzband/django-silk/issues/82)

**Closed issues:**

- base64 encoded responses break unit tests for Python3 [\#98](https://github.com/jazzband/django-silk/issues/98)
- Refactor Unit Tests to test new sort ordering structure. [\#96](https://github.com/jazzband/django-silk/issues/96)
- Running tests from the Travis config file fails because of difference in django-admin/manage.py [\#91](https://github.com/jazzband/django-silk/issues/91)
- Support for missing URL names in Django 1.8 and 1.9 [\#89](https://github.com/jazzband/django-silk/issues/89)
- UnicodeDecodeError in sql.py: leads to 500 internal error [\#85](https://github.com/jazzband/django-silk/issues/85)

**Merged pull requests:**

- remove simplejson [\#105](https://github.com/jazzband/django-silk/pull/105) ([digitaldavenyc](https://github.com/digitaldavenyc))
- Fixing Depreciation, Saving and Performance Tweaks [\#104](https://github.com/jazzband/django-silk/pull/104) ([Wrhector](https://github.com/Wrhector))
- Django 1.9 compatibility for the csrf context processor [\#100](https://github.com/jazzband/django-silk/pull/100) ([blag](https://github.com/blag))
- URL patterns are just Python lists for Django 1.9+ [\#99](https://github.com/jazzband/django-silk/pull/99) ([blag](https://github.com/blag))
- Refactor Unit Tests to test new sort ordering structure. [\#97](https://github.com/jazzband/django-silk/pull/97) ([trik](https://github.com/trik))
- Add Ascending/Descending sort order GET parameter in RequestsView [\#95](https://github.com/jazzband/django-silk/pull/95) ([trik](https://github.com/trik))
- Response bodies are now stored b64 encoded \(support for binary responses\). [\#94](https://github.com/jazzband/django-silk/pull/94) ([trik](https://github.com/trik))
- Unittests for models [\#93](https://github.com/jazzband/django-silk/pull/93) ([Alkalit](https://github.com/Alkalit))
- Conditional migration tests [\#92](https://github.com/jazzband/django-silk/pull/92) ([florisdenhengst](https://github.com/florisdenhengst))
- Added support for missing URL names in Django 1.8-1.9. [\#90](https://github.com/jazzband/django-silk/pull/90) ([florisdenhengst](https://github.com/florisdenhengst))
- Avoid errors when doing migrate command [\#86](https://github.com/jazzband/django-silk/pull/86) ([msaelices](https://github.com/msaelices))
- Namespace templatetags so they don't clash with existing application templatetags [\#81](https://github.com/jazzband/django-silk/pull/81) ([lmortimer](https://github.com/lmortimer))
- Added the use of Lambdas in settings.py to the README. [\#77](https://github.com/jazzband/django-silk/pull/77) ([bryson](https://github.com/bryson))

## [0.5.6](https://github.com/jazzband/django-silk/tree/0.5.6) (2015-09-06)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.5.5...0.5.6)

**Closed issues:**

- Post-processing static assets fails due to missing font files [\#51](https://github.com/jazzband/django-silk/issues/51)

**Merged pull requests:**

- Fixed report handling timing not included in meta-timing [\#76](https://github.com/jazzband/django-silk/pull/76) ([rodcloutier](https://github.com/rodcloutier))
- Support UUID in request headers [\#75](https://github.com/jazzband/django-silk/pull/75) ([rodcloutier](https://github.com/rodcloutier))
- test on latest django versions in travis [\#72](https://github.com/jazzband/django-silk/pull/72) ([nikolas](https://github.com/nikolas))

## [0.5.5](https://github.com/jazzband/django-silk/tree/0.5.5) (2015-06-04)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.5.3...0.5.5)

**Fixed bugs:**

- Pin six.py within silk to avoid version incompatibility. [\#70](https://github.com/jazzband/django-silk/issues/70)

**Closed issues:**

- IntegrityError: NOT NULL constraint failed: silk\_request.view\_name [\#71](https://github.com/jazzband/django-silk/issues/71)

## [0.5.3](https://github.com/jazzband/django-silk/tree/0.5.3) (2015-06-04)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.5.2...0.5.3)

**Closed issues:**

- null value in column "view\_name" violates not-null constraint [\#66](https://github.com/jazzband/django-silk/issues/66)
- Migrations do not work with Django 1.5.9 [\#64](https://github.com/jazzband/django-silk/issues/64)

**Merged pull requests:**

- It's not random, is it? [\#69](https://github.com/jazzband/django-silk/pull/69) ([peterbe](https://github.com/peterbe))
- Fix issue when view\_name was Null [\#67](https://github.com/jazzband/django-silk/pull/67) ([bartoszhernas](https://github.com/bartoszhernas))

## [0.5.2](https://github.com/jazzband/django-silk/tree/0.5.2) (2015-04-15)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.5.1...0.5.2)

**Merged pull requests:**

- Update model\_factory.py [\#62](https://github.com/jazzband/django-silk/pull/62) ([karabijavad](https://github.com/karabijavad))

## [0.5.1](https://github.com/jazzband/django-silk/tree/0.5.1) (2015-04-08)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.5...0.5.1)

**Implemented enhancements:**

- UTC time in templates [\#49](https://github.com/jazzband/django-silk/issues/49)

**Fixed bugs:**

- AttributeError: This StreamingHttpResponse instance has no `content` attribute [\#50](https://github.com/jazzband/django-silk/issues/50)

**Closed issues:**

- Django 1.8 support [\#55](https://github.com/jazzband/django-silk/issues/55)
- Should not have to manually add a logger for silk [\#53](https://github.com/jazzband/django-silk/issues/53)

## [0.5](https://github.com/jazzband/django-silk/tree/0.5) (2015-04-08)
[Full Changelog](https://github.com/jazzband/django-silk/compare/v0.4...0.5)

**Implemented enhancements:**

- 'thread.\_local' object has no attribute 'temp\_identifier' \(should log a warning stating that this is likely a middleware issue\) [\#52](https://github.com/jazzband/django-silk/issues/52)
- Check to see if process\_request of SilkyMiddleware has been called, and issue warnings on middleware placement if not [\#42](https://github.com/jazzband/django-silk/issues/42)
- Django 1.7 support [\#29](https://github.com/jazzband/django-silk/issues/29)

**Fixed bugs:**

- Django 1.5 support broken [\#60](https://github.com/jazzband/django-silk/issues/60)

**Closed issues:**

- Tests broken [\#61](https://github.com/jazzband/django-silk/issues/61)
- Deploying silk site-wide [\#56](https://github.com/jazzband/django-silk/issues/56)
- Migration error [\#54](https://github.com/jazzband/django-silk/issues/54)
- Silky doesn't work when django.middleware.gzip.GZipMiddleware is enabled [\#43](https://github.com/jazzband/django-silk/issues/43)
- static files not found problem [\#41](https://github.com/jazzband/django-silk/issues/41)
- No handlers could be found for logger "silk" [\#35](https://github.com/jazzband/django-silk/issues/35)

**Merged pull requests:**

- Add configuration option for custom intercept logic. [\#59](https://github.com/jazzband/django-silk/pull/59) ([kkaehler](https://github.com/kkaehler))
- commit\_on\_success -\> atomic, for 1.8, as commit\_on\_success was removed [\#58](https://github.com/jazzband/django-silk/pull/58) ([karabijavad](https://github.com/karabijavad))
- Update README.md [\#57](https://github.com/jazzband/django-silk/pull/57) ([karabijavad](https://github.com/karabijavad))
- Add a Gitter chat badge to README.md [\#48](https://github.com/jazzband/django-silk/pull/48) ([gitter-badger](https://github.com/gitter-badger))
- Tox integration added [\#47](https://github.com/jazzband/django-silk/pull/47) ([brmc](https://github.com/brmc))
- Edited ReadMe.md to avoid UnicodeDevodeError [\#44](https://github.com/jazzband/django-silk/pull/44) ([brmc](https://github.com/brmc))
- Added utf8 in curl query parameters [\#39](https://github.com/jazzband/django-silk/pull/39) ([ilvar](https://github.com/ilvar))
- Revert "Fix errors in manifest file" [\#37](https://github.com/jazzband/django-silk/pull/37) ([mtford90](https://github.com/mtford90))
- Fix IntegrityError caused by Request being saved 'None' raw\_body [\#36](https://github.com/jazzband/django-silk/pull/36) ([JannKleen](https://github.com/JannKleen))
- Fix errors in manifest file [\#34](https://github.com/jazzband/django-silk/pull/34) ([joaofrancese](https://github.com/joaofrancese))

## [v0.4](https://github.com/jazzband/django-silk/tree/v0.4) (2014-08-17)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.3.2...v0.4)

**Closed issues:**

- Live demo link is broken [\#30](https://github.com/jazzband/django-silk/issues/30)

**Merged pull requests:**

- Ability to not log every request, optimizations, db\_index, and a management command [\#31](https://github.com/jazzband/django-silk/pull/31) ([JoshData](https://github.com/JoshData))

## [0.3.2](https://github.com/jazzband/django-silk/tree/0.3.2) (2014-07-22)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.3.1...0.3.2)

**Fixed bugs:**

- No data profiled [\#25](https://github.com/jazzband/django-silk/issues/25)
- Incorrect interface for execute\_sql [\#24](https://github.com/jazzband/django-silk/issues/24)

**Closed issues:**

- Don't pin versions in setup.py [\#23](https://github.com/jazzband/django-silk/issues/23)
- Ability to clear old runs [\#14](https://github.com/jazzband/django-silk/issues/14)

**Merged pull requests:**

- Added tests for \_should\_intercept and fixed bug with requests not being ... [\#28](https://github.com/jazzband/django-silk/pull/28) ([mackeian](https://github.com/mackeian))
- Added missing requirement for running tests: mock [\#27](https://github.com/jazzband/django-silk/pull/27) ([mackeian](https://github.com/mackeian))

## [0.3.1](https://github.com/jazzband/django-silk/tree/0.3.1) (2014-07-05)
[Full Changelog](https://github.com/jazzband/django-silk/compare/0.3...0.3.1)

**Implemented enhancements:**

- Conform to charset flag in Content-Type header of request/response [\#20](https://github.com/jazzband/django-silk/issues/20)
- Enhance filtering  [\#17](https://github.com/jazzband/django-silk/issues/17)

**Fixed bugs:**

- Conform to charset flag in Content-Type header of request/response [\#20](https://github.com/jazzband/django-silk/issues/20)
- HttpRequest body has UTF-8 Character  causes UnicodeDecodeError ? [\#19](https://github.com/jazzband/django-silk/issues/19)

**Closed issues:**

- Problems with `six.moves.urllib` [\#22](https://github.com/jazzband/django-silk/issues/22)
- Incorrect string value: '\xCE\xBB, \xCF\x86...' for column 'raw\_body' at row 1 [\#21](https://github.com/jazzband/django-silk/issues/21)
- Silk fails on binary staticfiles content [\#16](https://github.com/jazzband/django-silk/issues/16)
- Silk's static assets are served from the wrong path [\#11](https://github.com/jazzband/django-silk/issues/11)

## [0.3](https://github.com/jazzband/django-silk/tree/0.3) (2014-06-17)
[Full Changelog](https://github.com/jazzband/django-silk/compare/V0.2.2...0.3)

## [V0.2.2](https://github.com/jazzband/django-silk/tree/V0.2.2) (2014-06-13)
[Full Changelog](https://github.com/jazzband/django-silk/compare/v0.2.2...V0.2.2)

## [v0.2.2](https://github.com/jazzband/django-silk/tree/v0.2.2) (2014-06-13)
[Full Changelog](https://github.com/jazzband/django-silk/compare/v0.2...v0.2.2)

**Closed issues:**

- request: timestamp on list of requests [\#15](https://github.com/jazzband/django-silk/issues/15)
- AttributeError: 'thread.\_local' object has no attribute 'temp\_identifier' [\#12](https://github.com/jazzband/django-silk/issues/12)

## [v0.2](https://github.com/jazzband/django-silk/tree/v0.2) (2014-06-12)
[Full Changelog](https://github.com/jazzband/django-silk/compare/v0.1.1...v0.2)

**Fixed bugs:**

- Stacktrace inspector allows users to see any file on the filesystem [\#10](https://github.com/jazzband/django-silk/issues/10)

## [v0.1.1](https://github.com/jazzband/django-silk/tree/v0.1.1) (2014-06-07)
[Full Changelog](https://github.com/jazzband/django-silk/compare/v0.1...v0.1.1)

**Closed issues:**

- Pip install direct from repo fails [\#9](https://github.com/jazzband/django-silk/issues/9)
- urls.py uses incorrect regex expressions [\#7](https://github.com/jazzband/django-silk/issues/7)
- requirements.txt must specify exact versions or version upper bounds [\#6](https://github.com/jazzband/django-silk/issues/6)
- Switch to PyPI for managing releases [\#4](https://github.com/jazzband/django-silk/issues/4)

**Merged pull requests:**

- Ensure README file is properly closed by setup.py [\#8](https://github.com/jazzband/django-silk/pull/8) ([svisser](https://github.com/svisser))
- updated readme [\#5](https://github.com/jazzband/django-silk/pull/5) ([rosscdh](https://github.com/rosscdh))

## [v0.1](https://github.com/jazzband/django-silk/tree/v0.1) (2014-06-06)


\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*⏎
