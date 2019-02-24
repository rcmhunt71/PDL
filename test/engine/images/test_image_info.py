from PDL.engine.images.image_info import Status, ImageData

from nose.tools import assert_equals


class TestImageInfo(object):

    FILENAME = 'filename.jpg'

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
        obj_1 = ImageData(image_id=self.FILENAME.split('.')[0])
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

        # Build ImageData object using class method
        test_image = ImageData.build_obj(dictionary=attr_dict)

        for attr, val in attr_dict.items():
            # Verify each attribute value matches the image object attribute value
            assert_equals(getattr(image, attr), getattr(test_image, attr))

            # Verify each attribute value matches the expected value (obj.attribute = ATTRIBUTE)
            assert_equals(getattr(test_image, attr), val)

    def test_build_obj_from_classmethod_with_extra_attributes(self):
        incorrect_attr = 'bogus_attr'

        image = ImageData()

        # Get list of attributes, and set base image values to obj.attribute = ATTRIBUTE
        attr_dict = dict([(x, x.upper()) for x in image._list_attributes() if not isinstance(x, list)])
        for attr, val in attr_dict.items():
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

                # Verify each attribute value matches the expected value (obj.attribute = ATTRIBUTE)
                assert_equals(getattr(test_image, attr), val)

    def test_build_obj_from_classmethod_without_id(self):
        image = ImageData()

        # Get list of attributes, and set base image values to obj.attribute = ATTRIBUTE
        attr_dict = dict([(x, x.upper()) for x in image._list_attributes() if not isinstance(x, list)])
        print(attr_dict.keys())
        del attr_dict[ImageData.ID]
        attr_dict[ImageData.FILENAME] = self.FILENAME
        for attr, val in attr_dict.items():
            setattr(image, attr, val)

        # Build ImageData object using class method
        test_image = ImageData.build_obj(dictionary=attr_dict)

        for attr, val in attr_dict.items():

            # Verify ID is defined as the filename without the extension
            if attr == ImageData.ID:
                assert_equals(getattr(test_image, ImageData.ID), self.FILENAME.split(',')[0])

            # Verify each attribute value matches the image object attribute value
            assert_equals(getattr(image, attr), getattr(test_image, attr))

            # Verify each attribute value matches the expected value (obj.attribute = ATTRIBUTE)
            assert_equals(getattr(test_image, attr), val)

    @staticmethod
    def _build_test_objs(description: str = "description_1",
                         status: str = Status.DOWNLOADED, name: str = 'obj_1', filename: str = FILENAME):

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
