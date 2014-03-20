"""
Tests for eventFinder.pyx

@author: `@parkin1`_
"""
import unittest
from pypore import cythonsetup
from pypore.event_finder import find_events
from pypore.event_finder import _get_data_range_test_wrapper
import numpy as np
import os
import pypore.filetypes.event_database as eD


class TestEventFinder(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_data_range_test_wrapper_at_new(self):
        n = 100
        first = np.zeros(n)
        first[n - 1] += 1.
        first[0] += 1.
        data_cache = [first, np.zeros(n) + 100., np.zeros(n) + 100. + 60., np.zeros(n) + 200.]

        res = _get_data_range_test_wrapper(data_cache, 0, n)
        self.assertEqual(res.size, n)
        np.testing.assert_array_equal(res, np.zeros(n) + 100.)

        # Test negative i to 0
        x = np.zeros(10)
        x[9] += 1.
        res = _get_data_range_test_wrapper(data_cache, -10, 0)
        np.testing.assert_array_equal(res, x)

        # Test negative i,n
        x = np.zeros(10)
        x[0] += 1.
        res = _get_data_range_test_wrapper(data_cache, -100, -90)
        np.testing.assert_array_equal(res, x)

        # Test negative i, pos n in first spot
        x = np.zeros(10)
        x[4] += 1.
        x[5:10] += 100.
        res = _get_data_range_test_wrapper(data_cache, -5, 5)
        np.testing.assert_array_equal(res, x)

        # Test pos i,n both in first spot
        x = np.zeros(10) + 100.
        res = _get_data_range_test_wrapper(data_cache, 60, 70)
        np.testing.assert_array_equal(res, x)

        # Test first and second cache overlap
        x = np.zeros(10) + 100.
        x[5:] += 60.
        res = _get_data_range_test_wrapper(data_cache, 95, 105)
        np.testing.assert_array_equal(res, x)

        # Test fist cache bumping up on second
        x = np.zeros(10) + 100.
        res = _get_data_range_test_wrapper(data_cache, 90, 100)
        np.testing.assert_array_equal(res, x)

        # Test second cache
        x = np.zeros(10) + 160.
        res = _get_data_range_test_wrapper(data_cache, 155, 165)
        np.testing.assert_array_equal(res, x)

        # Test neg overlap with 2 pos caches
        x = np.zeros(120)
        x[9] += 1.
        x[10:] += 100.
        x[110:] += 60.
        res = _get_data_range_test_wrapper(data_cache, -10, 110)

        # Test neg overlap with 3 pos caches
        x = np.zeros(220)
        x[9] += 1.
        x[10:] += 100.
        x[110:] += 60.
        x[210:] += 40.
        res = _get_data_range_test_wrapper(data_cache, -10, 210)

    def test_saving_files(self):
        filename = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(filename, 'testDataFiles', 'chimera_1event.log')

        event_database = find_events([filename], save_file_names=['_testSavingFiles_9238.h5'])[0]

        self.assertTrue(os.path.isfile(event_database))

        h5file = eD.open_file(event_database, mode='r')

        self.assertTrue(h5file.isopen)

        h5file.close()

        # delete the newly created event file
        os.remove(event_database)

    def test_chimera_no_noise_1event(self):
        filename = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(filename, 'testDataFiles', 'chimera_nonoise_1event.log')
        event_database = find_events([filename], save_file_names=['_testChimera_nonoise_1Event_9238.h5'])[0]

        h5file = eD.open_file(event_database, mode='r')

        events = h5file.root.events

        # check event table correct length        
        event_table = events.eventTable
        self.assertTrue(event_table.nrows, 1)

        # check raw data array correct length
        raw_data_matrix = events.rawData
        self.assertEqual(raw_data_matrix.nrows, 1)
        event_length = event_table[0]['eventLength']
        self.assertEqual(event_length, 1000)

        # Make sure only 1 event with 1 level
        levels_matrix = events.levels
        self.assertEqual(levels_matrix.nrows, 1)
        n_levels = event_table[0]['nLevels']
        self.assertEqual(n_levels, 1)
        levels = levels_matrix[0]
        self.assertAlmostEqual(levels[0], 0.9332, 4)

        # Check 1 event with 1 levelLength
        lengths_matrix = events.levelLengths
        self.assertEqual(lengths_matrix.nrows, 1)
        lengths = lengths_matrix[0]
        self.assertEqual(lengths[0], 1000)

        h5file.close()

        # delete the newly created event file
        os.remove(event_database)

    def _test_chimera_no_noise_1event_2levels_helper(self, h5file):
        events = h5file.root.events

        event_table = events.eventTable
        self.assertTrue(event_table.nrows, 1)

        # check raw data array correct length
        raw_data_matrix = events.rawData
        self.assertEqual(raw_data_matrix.nrows, 1)
        event_length = event_table[0]['eventLength']
        self.assertEqual(event_length, 1500)

        levels_matrix = events.levels
        self.assertEqual(levels_matrix.nrows, 1)
        levels = levels_matrix[0]
        n_levels = event_table[0]['nLevels']
        self.assertEqual(n_levels, 2)
        self.assertAlmostEqual(levels[0], 0.9332, 4)
        self.assertAlmostEqual(levels[1], 0.78064, 4)

        levels_matrix = events.levelLengths
        self.assertEqual(levels_matrix.nrows, 1)
        levels = h5file.get_level_lengths_at(0)
        self.assertEqual(len(levels), 2)
        self.assertEqual(levels[0], 750)
        self.assertEqual(levels[1], 750)

    def test_chimera_no_noise_1event_2levels(self):
        filename = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(filename, 'testDataFiles', 'chimera_nonoise_1event_2levels.log')
        event_database = find_events([filename], save_file_names=['_testChimera_nonoise_1Event_2Levels_9238.h5'])[0]

        h5file = eD.open_file(event_database, mode='r')
        self._test_chimera_no_noise_1event_2levels_helper(h5file)
        h5file.close()

        # delete the newly created event file
        os.remove(event_database)

    def _test_chimera_no_noise_2events_1levels_wrapper(self, h5file):
        events = h5file.root.events

        # check event table correct length        
        event_table = events.eventTable
        self.assertTrue(event_table.nrows, 2)

        # check raw data array correct length
        raw_data_matrix = events.rawData
        self.assertEqual(raw_data_matrix.nrows, 2)
        event_length = event_table[0]['eventLength']
        self.assertEqual(event_length, 1000)
        # second event
        event_length = event_table[1]['eventLength']
        self.assertEqual(event_length, 1000)

        # Make sure only 2 events with 1 level each
        levels_matrix = events.levels
        self.assertEqual(levels_matrix.nrows, 2)
        levels = levels_matrix[0]
        n_levels = event_table[0]['nLevels']
        self.assertEqual(n_levels, 1)
        self.assertAlmostEqual(levels[0], 0.9332, 4)
        # event 2
        levels = levels_matrix[1]
        n_levels_1 = event_table[1]['nLevels']
        self.assertEqual(n_levels_1, 1)
        self.assertAlmostEqual(levels[0], 0.9332, 4)

        # Check 2 events with 1 level -> 1 lengths
        lengths_matrix = events.levelLengths
        self.assertEqual(lengths_matrix.nrows, 2)
        lengths1 = h5file.get_level_lengths_at(0)
        self.assertEqual(len(lengths1), 1)
        self.assertEqual(lengths1[0], 1000)
        # event
        lengths2 = h5file.get_level_lengths_at(1)
        self.assertEqual(len(lengths2), 1)
        self.assertEqual(lengths2[0], 1000)

    def test_chimera_no_noise_2events_1levels(self):
        filename = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(filename, 'testDataFiles', 'chimera_nonoise_2events_1levels.log')
        event_databases = find_events([filename], save_file_names=['_testChimera_nonoise_2events_1levels_9238.h5'])

        self.assertEqual(len(event_databases), 1)

        event_database = event_databases[0]

        h5file = eD.open_file(event_database, mode='r')
        self._test_chimera_no_noise_2events_1levels_wrapper(h5file)
        h5file.close()

        # delete the newly created event file
        os.remove(event_database)

    def test_multiple_files(self):
        filename1 = os.path.dirname(os.path.realpath(__file__))
        filename1 = os.path.join(filename1, 'testDataFiles', 'chimera_nonoise_2events_1levels.log')
        filename2 = os.path.dirname(os.path.realpath(__file__))
        filename2 = os.path.join(filename2, 'testDataFiles', 'chimera_nonoise_1event_2levels.log')
        file_names = [filename1, filename2]
        event_databases = find_events(file_names,
                                      save_file_names=['_testMultipleFiles_1_9238.h5', '_testMultipleFiles_2_9238.h5'])

        self.assertEqual(len(event_databases), 2)

        h5file = eD.open_file(event_databases[0], mode='r')
        self._test_chimera_no_noise_2events_1levels_wrapper(h5file)
        h5file.close()
        os.remove(event_databases[0])

        h5file = eD.open_file(event_databases[1], mode='r')
        self._test_chimera_no_noise_1event_2levels_helper(h5file)
        h5file.close()
        os.remove(event_databases[1])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
