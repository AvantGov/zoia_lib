import os
import shutil
import unittest

import zoia_lib.backend.utilities as util
import zoia_lib.common.errors as errors

testing_path = os.getcwd()


class DeletionTest(unittest.TestCase):
    def setUp(self):
        util.backend_path = testing_path
        # Create a test patch to delete.
        util.add_test_patch("22222", 22222)

        # Create a secondary patch to ensure only the desired patch is deleted.
        util.add_test_patch("22223", 22223)

        # Create a version directory with 3 versions
        for i in range(1, 4):
            util.add_test_patch(os.path.join("22224", "22224_v{}".format(i)), 22224)

    def tearDown(self):
        # Clean up everything (in case it wasn't deleted properly).
        try:
            shutil.rmtree(os.path.join(testing_path, "22222"))
        except FileNotFoundError:
            pass
        try:
            os.remove(os.path.join(testing_path, "22222", "22222.bin"))
        except FileNotFoundError:
            pass
        try:
            os.remove(os.path.join(testing_path, "22222", "22222.json"))
        except FileNotFoundError:
            pass
        try:
            shutil.rmtree(os.path.join(testing_path, "22223"))
        except FileNotFoundError:
            pass
        try:
            os.remove(os.path.join(testing_path, "22223", "22223.bin"))
        except FileNotFoundError:
            pass
        try:
            os.remove(os.path.join(testing_path, "22223", "22223.json"))
        except FileNotFoundError:
            pass
        try:
            shutil.rmtree(os.path.join(testing_path, "22224"))
        except FileNotFoundError:
            pass
        try:
            for i in range(1, 4):
                os.remove(os.path.join(testing_path, "22224", "22224_v{}.bin".format(i)))
                os.remove(os.path.join(testing_path, "22224", "22224_v{}.bin".format(i)))
        except FileNotFoundError:
            pass

    def test_delete_patch_normal_local(self):
        """ Attempt to delete a patch that is stored in the
        backend ZoiaLibraryApp directory. The test ensures that
        the patch and metadata are deleted, along with the patch
        directory that contained the files.
        """

        self.setUp()

        # Try to break the method
        exc = (FileNotFoundError, errors.DeletionError)
        self.assertRaises(exc, util.delete_patch, "IamNotAPatch")
        self.assertRaises(exc, util.delete_patch, None)

        # Try to delete a patch that exists.
        try:
            util.delete_patch("22222")
        except errors.DeletionError:
            self.fail("Failed to find patch 22222 to delete.")

        # Ensure the deletion removed both 22222.bin and 22222.json
        for file in os.listdir(testing_path):
            self.assertFalse(file == "22222.bin" or file == "22222.json" or file == "22222",
                             "Deletion did not properly remove both the 22222 patch file, "
                             "associated metadata, and patch directory")

        # Check to make sure that no other files got deleted unexpectedly.
        self.assertFalse("22223" not in os.listdir(testing_path),
                         "Deletion also removed 22223 patch directory when it should not have.")
        self.assertFalse("22224" not in os.listdir(testing_path),
                         "Deletion also removed 22224 patch directory when it should not have.")
        for i in range(1, 4):
            self.assertTrue("22224_v{}.bin".format(i) in os.listdir(os.path.join(testing_path, "22224")),
                            "Deletion also removed patch file \"22224_v{}.bin\" when it should not have.".format(i))
            self.assertTrue("22224_v{}.json".format(i) in os.listdir(os.path.join(testing_path, "22224")),
                            "Deletion also removed patch file \"22224_v{}.json\" when it should not have.".format(i))

        self.tearDown()

    def test_delete_patch_version(self):
        """ Attempt to delete a patch that is stored in the
        backend ZoiaLibraryApp directory. This specific patch is
        contained within a version directory. The test ensures
        that  the patch and metadata are deleted. It also
        ensures only the correct version of a patch is deleted.

        Should the deletion result in a version directory with only
        one version remaining, the patch and metadata should be
        correctly renamed to drop the version suffix.

        Note: SD cards do not support the idea of patch version histories.
        As such, this test only applied to the locally stored patches on
        a user's machine and not those on an SD card.
        """

        self.setUp()
        # Try to delete a version.
        try:
            util.delete_patch(os.path.join("22224", "22224_v1"))
        except errors.DeletionError:
            self.fail("Failed to find patch 22224_v1 to delete.")

        # Ensure the deletion removed both 22224_v1.bin and 22224_v1.json
        for file in os.listdir(os.path.join(testing_path, "22224")):
            self.assertFalse(file == "22224_v1.bin" or file == "22224_v1.json",
                             "Deletion did not properly remove both the 22224_v1 patch file and associated metadata.")

        # Delete another version (which leaves only one version of the patch.
        try:
            util.delete_patch("22224_v2")
        except errors.DeletionError:
            self.fail("Failed to find patch 22224_v2 to delete.")

        # Ensure the remaining version of the patch was renamed properly.
        for patch in os.listdir(os.path.join(testing_path, "22224")):
            self.assertFalse(patch == "22224_v3.bin" or patch == "22224_v3.json" or patch == "22224",
                             "Deletion did not properly result in the renaming of the singularly "
                             "remaining patch version.")

        # Check to make sure that no other files got deleted unexpectedly.
        self.assertFalse("22222" not in os.listdir(testing_path),
                         "Deletion also removed 22222 patch directory when it should not have.")
        self.assertFalse("22223" not in os.listdir(testing_path),
                         "Deletion also removed 22223 patch directory when it should not have.")

        self.tearDown()

    def test_delete_patch_directory(self):
        self.setUp()

        # Try to break the method.
        exc = (FileNotFoundError, errors.DeletionError)
        self.assertRaises(exc, util.delete_full_patch_directory, "IamNotAPatch")
        self.assertRaises(exc, util.delete_full_patch_directory, None)
        self.assertRaises(exc, util.delete_full_patch_directory, "22222.bin")
        self.assertRaises(exc, util.delete_full_patch_directory, "22224_v1.bin")
        self.assertRaises(exc, util.delete_full_patch_directory, "22224_v1")

        # Try to delete a patch directory.
        util.delete_full_patch_directory("22222")
        self.assertFalse("22222" in os.listdir(testing_path),
                         "Deletion did not successfully remove patch directory 22222.")
        # Try to delete it again.
        self.assertRaises(exc, util.delete_full_patch_directory, "22222")

        # Try to delete a patch directory with multiple patches contained within.
        util.delete_full_patch_directory("22224")
        self.assertFalse("22224" in os.listdir(testing_path),
                         "Deletion did not successfully remove patch directory 22224.")
        try:
            for i in range(1, 4):
                self.assertTrue("22224_v{}.bin".format(i) in os.listdir(os.path.join(testing_path, "22224")),
                                "Deletion did not remove patch file \"22224_v{}.bin\".".format(i))
                self.assertTrue("22224_v{}.json".format(i) in os.listdir(os.path.join(testing_path, "22224")),
                                "Deletion did not remove patch file \"22224_v{}.json\".".format(i))
        except FileNotFoundError:
            pass

        self.tearDown()

    def test_delete_patch_normal_sd(self):
        """ Attempt to delete a patch that is stored on an
        inserted SD card.
        """
        # TODO Buy an SD card adapter and get to work on this.
        pass
