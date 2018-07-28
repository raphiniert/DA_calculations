# -*- coding: utf-8 -*-

"""
servo_motor_positioning.py contains the math for the master thesis' servo approach
"""

__author__ = "Raphael Kamper", "Jakob Blattner"

import numpy as np
import logging

# create logging basic conf to log files in log dir
logging.basicConfig(filename='log/servo_motor_positioning.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# logging according to: https://docs.python.org/3/howto/logging.html#logging-basic-tutorial

# create logger
logger = logging.getLogger('servo positioning')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def calculate_cent_difference(f1, f2):
    """
    calculates the difference of two frequencies f1 and f2 in cent
    :param f1: frequency 1 in Hertz
    :param f2: frequency 2 in Hertz
    :return: difference of f1 and f2 in cent
    """
    return 1200 * np.log2(f1 / f2 if f1 > f2 else f2 / f1)


def get_micros_as_degree(micros, precision=10.0, max_degrees=180.0):
    """
    TODO: implement this correctly
    :param micros:
    :param precision:
    :param max_degrees:
    :return:
    """
    return max_degrees * micros / max_degrees / precision if micros > 0 else 0.0


def calculate_alpha(a, b, beta):
    """
    calculates alpha by the law of sines. a/sin(alpha) = b/sin(beta)
    beta = arcsin((a * sin(beta))/b)
    :param a: length of a
    :param b: length of a
    :param beta: betain degree
    :return: alpha in degree
    """
    return np.rad2deg(np.arcsin((a * np.sin(np.deg2rad(beta))) / b))


def find_nearest_fret_points(points, frets):
    """
    Finds the nearest point to a given fret
    :param points: list of lenght values, degrees and deviations to the actual fret
    :param frets: list of fret positions
    :return: list with the according values to reach the nearest point to the fret
    """
    return [[i, min(points, key=lambda t: abs(t[5][i]))] for i, f in enumerate(frets)]


if __name__ == '__main__':
    logger.info("{0} START {0}".format("=" * 19))
    # setup the specs

    # music theory
    half_step_factor = 2 ** (1 / 12)  # twelfth root of 2

    # guitar
    mensur = 648.00  # mm
    max_frets = 13
    frets = [(mensur - (mensur / (half_step_factor ** f))) for f in range(1, max_frets + 1)]  # mm

    # string properties
    frequencies = [82.41, 110.0, 146.83, 196.0, 246.94, 329.63]  # Hz ... open strings frequency [E, A, D, G, H, e]
    wave_lengths = [(mensur - f) / 1000.0 * 2 for f in frets]  # m ... divide by 1000.0 to calc mm to m
    wave_speeds = [mensur / 1000.0 * 2 * fq for fq in frequencies]

    # calculating the frequencies per string per fret
    fret_frequencies = []
    for i, ws in enumerate(wave_speeds):
        fqs = [ws / wl for wl in wave_lengths]
        fret_frequencies.append([frequencies[i]] + fqs)
    logger.debug(fret_frequencies)

    # servo arm mounting
    a = 206.10  # mm
    b = 275.32  # mm

    e = 36.38  # mm
    f_offset = 50.00  # mm

    # servo motor specifications
    servo_min_micros = 600  # micro seconds
    servo_max_micros = 2400  # micro seconds
    servo_max_degrees = 180.0  # degree
    servo_dead_band = 2.0  # micro seconds
    servo_micro_seconds = servo_max_micros - servo_min_micros
    servo_precision = servo_micro_seconds / servo_max_degrees  # micro seconds

    # calculate
    points = []
    for ms in range(0, int(servo_micro_seconds + 1), int(servo_precision)):
        beta = get_micros_as_degree(ms)  # degree
        alpha = calculate_alpha(a, b, beta)  # degree
        gamma = 180.0 - alpha - beta  # degree
        c = (a ** 2 + b ** 2 - 2 * a * b * np.cos(np.deg2rad(gamma))) ** (1 / 2)  # calculated by the law of cosines
        f = (c ** 2 - e ** 2) ** (1 / 2) - f_offset  # calculated using the pythagorean law
        # print(alpha, beta, gamma, c, f)
        points.append([f, c, alpha, beta, gamma, [(f - fr) for fr in frets]])
    logger.debug(points)

    nearest_fret_points = find_nearest_fret_points(points, frets)
    logger.debug(nearest_fret_points)

    """ to create latex table
    # log fret, positions, frequencies and cent diff per fret
    logger.info("fret actual   nearest  actual   nearest   difference")
    logger.info("{0:2} & {1:6.2f} & {2:6.2f} & {3:6.2f} & {4:6.2f} & {5:5.2f}".format(
        0, 0.0, 0.0, fret_frequencies[0][0], fret_frequencies[0][0], 0.0))
    string_ind = 0  # E ... this is equal for all strings if all strings have the same mensur
    for i, f in enumerate(frets):
        ws = wave_speeds[string_ind]
        f1 = fret_frequencies[string_ind][i + 1]
        f2 = ws / ((mensur - nearest_fret_points[i][1][0]) / 1000.0 * 2)
        cent_diff = calculate_cent_difference(f1, f2)
        logger.info("{0:2} & {1:6.2f} & {2:6.2f} & {3:6.2f} & {4:6.2f} & {5:5.2f}".format(
            i + 1, f, nearest_fret_points[i][1][0], f1, f2, cent_diff))
    """

    # log fret, positions, frequencies, cent diff and geometric values per fret
    logger.info("fret actual   nearest  actual   nearest   diff    alpha    beta    gamma")
    logger.info("{0:2} & {1:6.2f} & {2:6.2f} & {3:6.2f} & {4:6.2f} & {5:5.2f} &   -    &   -    &   -    ".format(
        0, 0.0, 0.0, fret_frequencies[0][0], fret_frequencies[0][0], 0.0))
    string_ind = 0  # E ... this is equal for all strings if all strings have the same mensur
    for i, f in enumerate(frets):
        ws = wave_speeds[string_ind]
        f1 = fret_frequencies[string_ind][i + 1]
        f2 = ws / ((mensur - nearest_fret_points[i][1][0]) / 1000.0 * 2)
        cent_diff = calculate_cent_difference(f1, f2)
        logger.info("{0:2} & {1:6.2f} & {2:6.2f} & {3:6.2f} & {4:6.2f} & {5:5.2f} & {6:6.2f} & {7:6.2f} & {8:6.2f}".format(
            i + 1, f, nearest_fret_points[i][1][0], f1, f2, cent_diff, nearest_fret_points[i][1][2], nearest_fret_points[i][1][3], nearest_fret_points[i][1][4]))

    logger.info("{0} END {0}".format("=" * 20))
