from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from taxi.models import Manufacturer, Car, Driver

MANUFACTURER_URL = reverse("taxi:manufacturer-list")
CAR_URL = reverse("taxi:car-list")
DRIVER_URL = reverse("taxi:driver-list")


class PublicManufacturerTest(TestCase):
    def test_login_required(self):
        res = self.client.get(MANUFACTURER_URL)
        self.assertNotEqual(res.status_code, 200)


class PrivetManufacturerTest(TestCase):
    def setUp(self) -> None:
        self.driver = get_user_model().objects.create_user(
            username="driver",
            password="driver55"
        )
        self.client.force_login(self.driver)

    def test_retrieve_manufacturer_list(self):
        Manufacturer.objects.create(name="test_1", country="test_country")
        Manufacturer.objects.create(name="test_2", country="country")
        res = self.client.get(MANUFACTURER_URL)
        self.assertEqual(res.status_code, 200)
        manufacturers = Manufacturer.objects.all()
        self.assertEqual(
            list(res.context["manufacturer_list"]),
            list(manufacturers)
        )
        self.assertTemplateUsed(res, "taxi/manufacturer_list.html")


class PublicCarTest(TestCase):
    def test_login_required(self):
        res = self.client.get(CAR_URL)
        self.assertNotEqual(res.status_code, 200)


class PrivetCarTest(TestCase):
    def setUp(self) -> None:
        self.driver = get_user_model().objects.create_user(
            username="driver",
            password="driver55"
        )
        self.manufacturer = Manufacturer.objects.create(
            name="test",
            country="country"
        )
        self.client.force_login(self.driver)

    def test_retrieve_car_list(self):
        car = Car.objects.create(
            model="test_model",
            manufacturer=self.manufacturer
        )
        car.drivers.add(self.driver)
        car_1 = Car.objects.create(
            model="model_1",
            manufacturer=self.manufacturer
        )
        car_1.drivers.add(self.driver)
        res = self.client.get(CAR_URL)
        self.assertEqual(res.status_code, 200)
        cars = Car.objects.all()
        self.assertEqual(
            list(res.context["car_list"]),
            list(cars)
        )
        self.assertTemplateUsed(res, "taxi/car_list.html")


class PublicDriverTest(TestCase):
    def test_login_required(self):
        res = self.client.get(DRIVER_URL)
        self.assertNotEqual(res.status_code, 200)


class PrivetDriverTest(TestCase):
    def setUp(self):
        self.driver = Driver.objects.create(
            username="testdrive",
            password="drive123"
        )
        self.driver_1 = Driver.objects.create(
            username="driver",
            password="test999",
            license_number="OOO88888"
        )
        self.client.force_login(self.driver)

    def test_retrieve_driver_list(self):
        res = self.client.get(DRIVER_URL)
        self.assertEqual(res.status_code, 200)
        drivers = Driver.objects.all()
        self.assertEqual(
            list(res.context["driver_list"]),
            list(drivers)
        )
        self.assertTemplateUsed(res, "taxi/driver_list.html")
