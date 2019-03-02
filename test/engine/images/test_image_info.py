import os

from PDL.engine.images.image_info import Status, ImageData

from nose.tools import assert_equals

EXTRA_DIR = 'extra_dir'
DL_DIR = os.path.sep.join([os.getcwd(), 'test', 'data'])


class TestImageInfo(object):

    IMAGE_EXT = 'jpg'
    DNE_FILENAME = f'filename.{IMAGE_EXT}'
    EXISTS_FILENAME = f'image.{IMAGE_EXT}'

    def test_add_obj_return_new(self):
        obj_1 = ImageData()
        obj_2 = ImageData()

        obj_3 = obj_1 + obj_2

        assert_equals(obj_3.filename, obj_2.filename)
        assert_equals(obj_3.id, obj_1.id)
        assert_equals(obj_3.description, obj_1.description)
        assert_equals(obj_3.dl_status, obj_1.dl_status)
        assert_equals(obj_3.image_name, obj_1.image_name)

    def test_add_obj_return_new_using_combine(self):
        obj_1 = ImageData(image_id=self.DNE_FILENAME.split('.')[0])
        obj_2 = ImageData()

        obj_3 = obj_1.combine(other=obj_2, use_self=False)

        assert_equals(obj_3.id, obj_1.id)
        assert_equals(obj_3.filename, obj_1.filename)
        assert_equals(obj_3.description, obj_1.description)
        assert_equals(obj_3.dl_status, obj_1.dl_status)
        assert_equals(obj_3.image_name, obj_1.image_name)

    def test_add_obj_return_self(self):

        obj_1_description = "Desc1"
        obj_1_status = Status.DOWNLOADED
        obj_1_name = 'obj_1'

        obj_1, obj_2 = self._build_test_objs(
            description=obj_1_description, status=obj_1_status, name=obj_1_name)

        obj_1 += obj_2

        assert_equals(obj_1.filename, obj_2.filename)
        assert_equals(obj_1.id, obj_2.id)
        assert_equals(obj_1.description, obj_1_description)
        assert_equals(obj_1.dl_status, obj_1_status)
        assert_equals(obj_1.author, 'author_2')
        assert_equals(obj_1.image_name, obj_1_name)

    def test_convert_to_dict(self):
        image = ImageData()
        attr_dict = dict([(x, x.upper()) for x in image._list_attributes() if not isinstance(x, list)])
        for attr, val in attr_dict.items():
            setattr(image, attr, val)

        image_dict = image.to_dict()
        assert_equals(attr_dict, image_dict)

    def test_build_obj_from_classmethod(self):
        image = ImageData()

        # Get list of attributes, and set base image values to obj.attribute = ATTRIBUTE
        attr_dict = dict([(x, x.upper()) for x in image._list_attributes() if not isinstance(x, list)])
        for attr, val in attr_dict.items():
            setattr(image, attr, val)
            if attr.lower() == 'filename':
                image.filename += f".{self.IMAGE_EXT}"

        # Build ImageData object using class method
        test_image = ImageData.build_obj(dictionary=attr_dict)

        for attr, val in attr_dict.items():
            # Verify each attribute value matches the image object attribute value
            assert_equals(getattr(image, attr), getattr(test_image, attr))

            # Code automatically appends image extension to filename if missing.
            if attr.lower() == 'filename':
                val += f".{self.IMAGE_EXT}"

            # Verify each attribute value matches the expected value (obj.attribute = ATTRIBUTE)
            assert_equals(getattr(test_image, attr), val)

    def test_build_obj_from_classmethod_with_extra_attributes(self):
        incorrect_attr = 'bogus_attr'

        image = ImageData()

        # Get list of attributes, and set base image values to obj.attribute = ATTRIBUTE
        attr_dict = dict([(x, x.upper()) for x in image._list_attributes() if not isinstance(x, list)])
        for attr, val in attr_dict.items():
            # Code automatically appends image extension to filename if missing.
            if attr.lower() == 'filename':
                val += f".{self.IMAGE_EXT}"

            setattr(image, attr, val)
        attr_dict[incorrect_attr] = incorrect_attr.upper()

        # Build ImageData object using class method
        test_image = ImageData.build_obj(dictionary=attr_dict)

        for attr, val in attr_dict.items():

            # This attribute should not exist/be defined
            if attr == incorrect_attr:
                assert(not hasattr(test_image, incorrect_attr))

            else:
                # Verify each attribute value matches the image object attribute value
                assert_equals(getattr(image, attr), getattr(test_image, attr))

                # Code automatically appends image extension to filename if missing.
                if attr.lower() == 'filename':
                    val += f".{self.IMAGE_EXT}"

                # Verify each attribute value matches the expected value (obj.attribute = ATTRIBUTE)
                assert_equals(getattr(test_image, attr), val)

    def test_build_obj_from_classmethod_without_id(self):
        image = ImageData()

        # Get list of attributes, and set base image values to obj.attribute = ATTRIBUTE
        attr_dict = dict([(x, x.upper()) for x in image._list_attributes() if not isinstance(x, list)])
        print(attr_dict.keys())
        del attr_dict[ImageData.ID]
        attr_dict[ImageData.FILENAME] = self.DNE_FILENAME
        for attr, val in attr_dict.items():
            setattr(image, attr, val)

        # Build ImageData object using class method
        test_image = ImageData.build_obj(dictionary=attr_dict)

        for attr, val in attr_dict.items():

            # Verify ID is defined as the filename without the extension
            if attr == ImageData.ID:
                assert_equals(getattr(test_image, ImageData.ID), self.DNE_FILENAME.split(',')[0])

            # Verify each attribute value matches the image object attribute value
            assert_equals(getattr(image, attr), getattr(test_image, attr))

            # Verify each attribute value matches the expected value (obj.attribute = ATTRIBUTE)
            assert_equals(getattr(test_image, attr), val)

    def test_verify_locations_dne(self):
        image_path = DL_DIR

        obj_1 = ImageData()
        obj_1.filename = self.DNE_FILENAME
        obj_1.locations.append(image_path)
        valid_locations = obj_1._verify_locations(obj_1)
        assert_equals(valid_locations, [])

    def test_image_data_table(self):
        # Verify table is built without throwing errors. Not verifying table contents at this time.

        # TODO: Create routine to validate contents of string (use here and stringify validation)

        img_1, _ = self._build_test_objs()
        table_1 = img_1.table()

        assert(isinstance(table_1, str))

    def test_image_data_stringify(self):
        # Verify table is built without throwing errors. Not verifying table contents at this time.
        img_1, _ = self._build_test_objs()
        table_1 = str(img_1)
        assert(isinstance(table_1, str))

    def test_original_obj_location_exists_other_location_not_set_original_not_overwritten(self):
        img_1, img_2 = self._build_test_objs(filename=self.EXISTS_FILENAME)
        img_1.locations.append(DL_DIR)
        img_3 = img_1.combine(other=img_2)
        assert_equals(len(img_3.locations), 1)
        assert_equals(img_3.locations[0], DL_DIR)

    def test_original_obj_location_not_set_other_obj_location_set_location_added(self):
        img_1, img_2 = self._build_test_objs(filename=self.EXISTS_FILENAME)
        img_2.locations.append(DL_DIR)
        img_3 = img_1.combine(other=img_2)
        assert_equals(len(img_3.locations), 1)
        assert_equals(img_3.locations[0], DL_DIR)

    def test_original_obj_location_exists_other_obj_location_matches_not_duplicated(self):
        img_1, img_2 = self._build_test_objs(filename=self.EXISTS_FILENAME)
        img_1.locations.append(DL_DIR)
        img_2.locations.append(DL_DIR)
        img_3 = img_1.combine(other=img_2)
        assert_equals(len(img_3.locations), 1)
        assert_equals(img_3.locations[0], DL_DIR)

    def test_original_obj_location_set_but_dne_other_obj_location_valid(self):
        img_1, img_2 = self._build_test_objs(filename=self.EXISTS_FILENAME)
        img_1.locations.append(os.path.sep.join(['.', 'dir', 'does', 'not', 'exist']))
        img_2.locations.append(DL_DIR)
        img_3 = img_1.combine(other=img_2)
        assert_equals(len(img_3.locations), 1)
        assert_equals(img_3.locations[0], DL_DIR)

    def test_original_obj_location_set_other_obj_location_set_and_valid_but_different(self):
        img_1, img_2 = self._build_test_objs(filename=self.EXISTS_FILENAME)
        other_file_loc = os.path.sep.join([DL_DIR, EXTRA_DIR])
        img_1.locations.append(DL_DIR)
        img_2.locations.append(other_file_loc)
        img_3 = img_1.combine(other=img_2)
        assert_equals(len(img_3.locations), 2)
        assert DL_DIR in img_3.locations
        assert other_file_loc in img_3.locations

    @staticmethod
    def _build_test_objs(description: str = "description_1",
                         status: str = Status.DOWNLOADED, name: str = 'obj_1', filename: str = DNE_FILENAME):

        obj_1 = ImageData()
        obj_2 = ImageData()

        obj_1.description = description
        obj_1.dl_status = status
        obj_1.image_name = name
        obj_1.filename = filename
        obj_1.id = filename.split('.')[0]

        obj_2.filename = filename
        obj_2.author = 'author_2'
        obj_2.image_name = 'obj_2'
        obj_2.id = filename.split('.')[0]
        return obj_1, obj_2
