from PDL.engine.images.image_info import Status, ImageData

from nose.tools import assert_equals


class TestImageInfo(object):
    def test_add_obj(self):
        obj_1 = ImageData()
        obj_2 = ImageData()

        obj_1.description = "Desc1"
        obj_1.dl_status = Status.DOWNLOADED

        obj_2.filename = 'filename_2'
        obj_2.id = 'image_2'

        obj_3 = obj_1 + obj_2
        assert_equals(obj_3.filename, obj_2.filename)
        assert_equals(obj_3.id, obj_2.id)
        assert_equals(obj_3.description, obj_1.description)
        assert_equals(obj_3.dl_status, obj_1.dl_status)
