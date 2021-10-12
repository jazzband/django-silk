import random

from django.test import TestCase
from unittest.mock import Mock

from .test_lib.mock_suite import MockSuite
from silk.views.profiling import ProfilingView


class TestProfilingViewDefaults(TestCase):
    def test_func_names(self):
        profiles = [MockSuite().mock_profile() for _ in range(0, 3)]
        func_names = ProfilingView()._get_function_names()
        for p in profiles:
            self.assertIn(p.func_name, func_names)
        self.assertIn("", func_names)

    def test_show(self):
        self.assertIn(ProfilingView.default_show, ProfilingView.show)

    def test_order_by(self):
        self.assertIn(ProfilingView.defualt_order_by, ProfilingView.order_by)


class TestProfilingViewGetObjects(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestProfilingViewGetObjects, cls).setUpClass()
        cls.profiles = [MockSuite().mock_profile() for _ in range(0, 10)]

    def test_ordering(self):
        results = ProfilingView()._get_objects(order_by="Recent")
        self.assertSorted(results, "start_time")

    def test_show(self):
        results = ProfilingView()._get_objects(show=5)
        self.assertEqual(5, len(results))

    def test_func_name(self):
        func_name = "a_func_name"
        self.profiles[1].func_name = func_name
        self.profiles[1].save()
        results = ProfilingView()._get_objects(func_name=func_name)
        for r in results:
            self.assertEqual(r.func_name, func_name)

    def assertSorted(self, objects, sort_field):
        for idx, r in enumerate(objects):
            try:
                nxt = objects[idx + 1]
                self.assertGreaterEqual(
                    getattr(r, sort_field), getattr(nxt, sort_field)
                )
            except IndexError:
                pass


class TestProfilingContext(TestCase):
    def test_default(self):
        request = Mock(spec_set=["GET", "session"])
        request.GET = {}
        request.session = {}
        context = ProfilingView()._create_context(request)
        self.assertDictContainsSubset(
            {
                "show": ProfilingView.default_show,
                "order_by": ProfilingView.defualt_order_by,
                "options_show": ProfilingView.show,
                "options_order_by": ProfilingView.order_by,
                "options_func_names": ProfilingView()._get_function_names(),
            },
            context,
        )
        self.assertNotIn("path", context)
        self.assertIn("results", context)

    def test_get(self):
        request = Mock(spec_set=["GET", "session"])
        request.session = {}
        show = 10
        func_name = "func_name"
        name = "name"
        order_by = "Time"
        request.GET = {
            "show": show,
            "func_name": func_name,
            "name": name,
            "order_by": order_by,
        }
        context = ProfilingView()._create_context(request)
        self.assertDictContainsSubset(
            {
                "show": show,
                "order_by": order_by,
                "func_name": func_name,
                "name": name,
                "options_show": ProfilingView.show,
                "options_order_by": ProfilingView.order_by,
                "options_func_names": ProfilingView()._get_function_names(),
            },
            context,
        )
        self.assertIn("results", context)
