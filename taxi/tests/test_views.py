from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.forms import ManufacturerSearchForm, CarSearchForm, DriverSearchForm
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
        self.manufacturer = Manufacturer.objects.create(
            name="manufacturer test",
            country="Country"
        )

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

    def test_create_manufacturer(self):
        response = self.client.post(
            reverse("taxi:manufacturer-create"),
            {"name": "New Manufacturer", "country": "Country"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Manufacturer.objects.filter(name="New Manufacturer").exists()
        )

    def test_update_manufacturer(self):
        form_data = {
            "name": "Updated manufacturer",
            "country": self.manufacturer.country
        }
        response = self.client.post(
            reverse("taxi:manufacturer-update", args=[self.manufacturer.id]),
            form_data
        )
        self.assertEqual(response.status_code, 302)
        self.manufacturer.refresh_from_db()
        self.assertEqual(self.manufacturer.name, "Updated manufacturer")

    def test_delete_manufacturer(self):
        self.manufacturer = Manufacturer.objects.create(
            name="Manufacturer to delete"
        )
        response = self.client.post(
            reverse("taxi:manufacturer-delete", args=[self.manufacturer.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Manufacturer.objects.filter(
                name="Manufacturer to delete"
            ).exists())


class ManufacturerSearchFormTest(TestCase):
    def test_valid_data(self):
        form = ManufacturerSearchForm(data={"name": "Test Manufacturer"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Test Manufacturer")

    def test_empty_data(self):
        form = ManufacturerSearchForm(data={})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "")


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

    def test_create_car(self):
        response = self.client.post(reverse("taxi:car-create"), {
            "model": "New Car",
            "manufacturer": self.manufacturer.id,
            "drivers": self.driver.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Car.objects.filter(model="New Car").exists())

    def test_update_car(self):
        car = Car.objects.create(
            model="Car",
            manufacturer=self.manufacturer,
        )
        car.drivers.set([self.driver.id])
        form_data = {
            "model": "new car",
            "manufacturer": self.manufacturer.id,
            "drivers": self.driver.id
        }
        resp = self.client.post(
            reverse("taxi:car-update", args=[car.id]),
            form_data
        )

        self.assertEqual(resp.status_code, 302)
        car.refresh_from_db()
        self.assertEqual(car.model, "new car")

    def test_delete_car(self):
        car = Car.objects.create(
            model="Car to Delete",
            manufacturer=self.manufacturer
        )
        response = self.client.post(reverse("taxi:car-delete", args=[car.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Car.objects.filter(id=car.id).exists())


class CarSearchFormTest(TestCase):
    def test_valid_data(self):
        form = CarSearchForm(data={"model": "Test Model"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["model"], "Test Model")

    def test_empty_data(self):
        form = CarSearchForm(data={})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["model"], "")


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

    def test_create_driver(self):
        form_data = {
            "username": "new_driver",
            "password1": "pas4268word",
            "password2": "pas4268word",
            "license_number": "GHP23456",
            "first_name": "Drive",
            "last_name": "Test",
        }
        response = self.client.post(reverse("taxi:driver-create"), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Driver.objects.filter(username="new_driver").exists())

    def test_update_driver_license(self):
        response = self.client.post(
            reverse("taxi:driver-update", args=[self.driver.id]),
            {"license_number": "ZXF87654"}
        )
        self.assertEqual(response.status_code, 302)
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.license_number, "ZXF87654")

    def test_delete_driver(self):
        response = self.client.post(
            reverse("taxi:driver-delete", args=[self.driver_1.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Driver.objects.filter(id=self.driver_1.id).exists())


class DriverSearchFormTest(TestCase):
    def test_valid_data(self):
        form = DriverSearchForm(data={"username": "TestDriver"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], "TestDriver")

    def test_empty_data(self):
        form = DriverSearchForm(data={})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], "")
