#!/usr/bin/env python3
"""Merge Fatawa Razviya Jild 11 easy-Urdu tashreeh v4 chunks into jild-11.json.

Reads the 15 leaf chunk files listed in chunks-manifest-v4-jild11.json,
concatenates them in order 01 -> 02 -> 03 -> 04a -> 04b -> 05a -> 05b ->
06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13, derives start_page =
min(pages) where the field is absent, normalises page markers,
validates, and writes {"masail": [...]} to jild-11.json.

ORDER -- chunk order is the order:
  The v3 merged file ~/workspace/fatawa-app/content/tashreeh/jild-11.json
  has ID order == concatenation order of the v4 leaf chunks (verified
  locally by the coordinator: all 394 ids match the v3 sequence exactly).
  Do NOT sort or reorder. Within each chunk, items keep file order.
  CHUNK_ORDER is an explicit list because leaves 04a/04b and 05a/05b
  break the numeric range pattern.

BOUNDARY DEDUP (11 masail — the Jild 10 masala-87 pattern, repeated):
  the v3 chunk files overlap by one item at 11 boundaries; the merged
  v3 has each ONCE with combined pages + combined notes. Each boundary
  masala is written ONCE, in the EARLIER leaf, combining both halves'
  tashreeh into one flowing passage with ALL notes from both halves:
  masala-8 (leaf 02), masala-16 (leaf 02), masala-46 (leaf 03),
  masala-135 (leaf 04b), masala-201 (leaf 06), masala-255 (leaf 07),
  masala-287 (leaf 08), masala-325 (leaf 09), masala-342 (leaf 10),
  masala-394 (leaf 11), masala-437 (leaf 12). The LATER leaf EXCLUDES
  the boundary masala. Leaf page ranges overlap at 10 shared pages
  (242, 275, 292, 325, 459, 509, 559, 609, 663, 713 — consecutive items
  sharing a page), so per-leaf present pages sum to 636 while the
  merged file has 626 UNIQUE pages. Those are v3 ids, kept exactly —
  they are NOT merge renames.

NO RENAME QUIRK in Jild 11: the v3 merged file has 394 UNIQUE ids — the
  book numbers no masala twice in this jild (unlike Jild 5, which had
  two masail 263 and two masail 304, and Jild 6, which had two masail
  774). Chunk ids are used exactly as written; the merge asserts
  duplicate-free ids instead of renaming anything.
  NOTE: v3 has split files 04a/04b and 05a/05b — each pair was split by
  the coordinator to keep every leaf <= 48 items (leaf 04a = 48 items,
  leaf 05a = 27, 05b = 26). Leaf 01 has only 33 pages present in
  pp.6-141 (big source gaps). The combined-range id
  jild9-masala-85-87 is a Jild 9 id, NOT Jild 11 — Jild 11 has no
  combined-range ids of that form; its first id is the page item
  jild11-pesh-lafz (pages [6, 7]).

START_PAGE: every one of the 15 v4 leaf chunks carries start_page ==
  min(pages) for all its items (verified by the coordinator). The
  derivation code below stays as a safety net; it is expected to
  derive 0 items.

MARKER NORMALISATION (the only text transformation): page markers, if
  present, are normalised to the single form [safha N] written with the
  Urdu word for page:
  - lenticular-bracket form (U+3010/U+3011 around the Urdu word for
    page + number) -> [safha N]
  - [short form] -> [safha N]
  - [safha N] stays as-is
  Applied to every string field of every item (jawab, sawal, title,
  notes). The 15 v4 chunks contain ZERO markers of any form (verified
  locally), so normalisation is expected to be a no-op here; the code
  stays so the merge is robust and the "none remain" assertions still
  run. No other text is touched and no markers are invented.
  NOTE: the literal lenticular-bracket characters are written here only
  as U+3010/U+3011 escapes, never as literal characters in this file.

VALIDATION (fails loudly on any violation):
  394 items; ID sequence EXACTLY == the v3 merged file's ID sequence
  (embedded below as V3_IDS, copied verbatim from
  ~/workspace/fatawa-app/content/tashreeh/jild-11.json); pages per item
  identical to v3 (embedded as V3_PAGES, same source, verified against
  the v3 file before pushing); 626 unique pages (min 6, max 739);
  volume_ids == {54}; start_page == min(pages) for every item (after
  derivation); zero empty tashreeh_jawab; no lenticular / short markers
  remain; first id jild11-pesh-lafz, last id jild11-masala-459.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = "chunks-manifest-v4-jild11.json"

# Concatenation order: chunk files 01 -> 18, in order.
CHUNK_ORDER = ["jild-11-chunk-01.json", "jild-11-chunk-02.json", "jild-11-chunk-03.json", "jild-11-chunk-04a.json", "jild-11-chunk-04b.json", "jild-11-chunk-05a.json", "jild-11-chunk-05b.json", "jild-11-chunk-06.json", "jild-11-chunk-07.json", "jild-11-chunk-08.json", "jild-11-chunk-09.json", "jild-11-chunk-10.json", "jild-11-chunk-11.json", "jild-11-chunk-12.json", "jild-11-chunk-13.json"]

EXPECTED_ITEMS = 394
EXPECTED_PAGES = 626
EXPECTED_MIN_PAGE = 6
EXPECTED_MAX_PAGE = 739
EXPECTED_VOLUME_IDS = {54}
EXPECTED_FIRST_ID = "jild11-pesh-lafz"
EXPECTED_LAST_ID = "jild11-masala-459"

# v3 ID sequence, verbatim from content/tashreeh/jild-11.json.
V3_IDS = ['jild11-pesh-lafz', 'jild11-masala-1', 'jild11-masala-2', 'jild11-masala-3', 'jild11-masala-4', 'jild11-masala-5-6', 'jild11-p142', 'jild11-masala-7', 'jild11-masala-8', 'jild11-masala-9', 'jild11-masala-10', 'jild11-masala-11', 'jild11-masala-12', 'jild11-masala-13', 'jild11-masala-14-15', 'jild11-masala-16', 'jild11-masala-17', 'jild11-masala-18', 'jild11-masala-19', 'jild11-masala-20', 'jild11-masala-21', 'jild11-masala-22', 'jild11-masala-23', 'jild11-masala-24', 'jild11-masala-25', 'jild11-masala-26', 'jild11-masala-27', 'jild11-masala-28', 'jild11-masala-29', 'jild11-masala-30', 'jild11-masala-31', 'jild11-masala-32', 'jild11-masala-33', 'jild11-masala-34', 'jild11-masala-35', 'jild11-masala-36', 'jild11-masala-37', 'jild11-masala-38', 'jild11-masala-39', 'jild11-masala-40', 'jild11-masala-41', 'jild11-masala-42', 'jild11-masala-43-44', 'jild11-masala-45', 'jild11-masala-46', 'jild11-masala-47', 'jild11-masala-48', 'jild11-masala-49', 'jild11-masala-50', 'jild11-masala-51', 'jild11-masala-53', 'jild11-masala-54', 'jild11-masala-55', 'jild11-masala-56', 'jild11-masala-57', 'jild11-masala-58', 'jild11-masala-59', 'jild11-masala-60', 'jild11-masala-61', 'jild11-masala-62', 'jild11-masala-63', 'jild11-masala-64', 'jild11-masala-65', 'jild11-masala-66', 'jild11-masala-73', 'jild11-masala-74', 'jild11-masala-75', 'jild11-masala-76', 'jild11-masala-77', 'jild11-masala-78', 'jild11-masala-79', 'jild11-masala-81', 'jild11-masala-82', 'jild11-masala-83', 'jild11-masala-84', 'jild11-masala-85', 'jild11-masala-87', 'jild11-masala-88', 'jild11-masala-89', 'jild11-masala-90', 'jild11-masala-92', 'jild11-masala-93', 'jild11-masala-94', 'jild11-masala-95', 'jild11-masala-96', 'jild11-masala-97', 'jild11-masala-98', 'jild11-masala-99', 'jild11-masala-100', 'jild11-masala-101', 'jild11-masala-102', 'jild11-masala-103', 'jild11-masala-104', 'jild11-p275', 'jild11-masala-107', 'jild11-masala-108', 'jild11-masala-109', 'jild11-masala-112', 'jild11-masala-113', 'jild11-masala-114', 'jild11-masala-115', 'jild11-masala-117', 'jild11-masala-118', 'jild11-masala-119', 'jild11-masala-120', 'jild11-masala-121', 'jild11-masala-122', 'jild11-masala-128', 'jild11-masala-129', 'jild11-masala-130', 'jild11-masala-131', 'jild11-masala-132', 'jild11-masala-133', 'jild11-masala-135', 'jild11-masala-136', 'jild11-masala-137', 'jild11-masala-138', 'jild11-masala-139', 'jild11-masala-140', 'jild11-masala-141', 'jild11-masala-142', 'jild11-masala-143', 'jild11-masala-144-147', 'jild11-masala-148', 'jild11-masala-149', 'jild11-masala-150', 'jild11-masala-152', 'jild11-masala-153', 'jild11-masala-154', 'jild11-p313', 'jild11-masala-155', 'jild11-masala-156', 'jild11-masala-157', 'jild11-masala-158', 'jild11-masala-159', 'jild11-masala-160', 'jild11-masala-161', 'jild11-masala-162', 'jild11-masala-163', 'jild11-masala-164', 'jild11-masala-165', 'jild11-masala-166', 'jild11-masala-167', 'jild11-masala-168', 'jild11-masala-169', 'jild11-masala-170', 'jild11-masala-171', 'jild11-masala-172', 'jild11-masala-173', 'jild11-masala-174', 'jild11-masala-175', 'jild11-masala-176-177', 'jild11-masala-178', 'jild11-masala-179', 'jild11-masala-180', 'jild11-masala-181', 'jild11-masala-182', 'jild11-masala-183', 'jild11-masala-184', 'jild11-masala-185', 'jild11-masala-186-188', 'jild11-masala-189', 'jild11-masala-190', 'jild11-masala-191', 'jild11-masala-192', 'jild11-masala-193', 'jild11-masala-194', 'jild11-masala-195', 'jild11-masala-196', 'jild11-masala-197', 'jild11-masala-198', 'jild11-masala-199', 'jild11-masala-200', 'jild11-masala-201', 'jild11-masala-202', 'jild11-masala-203', 'jild11-masala-204', 'jild11-masala-205', 'jild11-masala-209', 'jild11-masala-210', 'jild11-masala-211', 'jild11-masala-213', 'jild11-masala-214', 'jild11-masala-215', 'jild11-masala-216', 'jild11-masala-217', 'jild11-masala-218', 'jild11-masala-219', 'jild11-masala-220', 'jild11-masala-221', 'jild11-masala-222', 'jild11-masala-223', 'jild11-masala-227', 'jild11-masala-228', 'jild11-masala-229', 'jild11-masala-232', 'jild11-masala-234', 'jild11-masala-235', 'jild11-masala-236', 'jild11-masala-237', 'jild11-masala-238', 'jild11-masala-239', 'jild11-masala-240', 'jild11-masala-241', 'jild11-masala-242', 'jild11-masala-243', 'jild11-masala-244', 'jild11-masala-245', 'jild11-masala-246', 'jild11-masala-247', 'jild11-masala-248', 'jild11-masala-249', 'jild11-masala-250', 'jild11-masala-251', 'jild11-masala-252', 'jild11-masala-253', 'jild11-masala-254', 'jild11-masala-255', 'jild11-masala-256', 'jild11-masala-257', 'jild11-masala-258', 'jild11-masala-259', 'jild11-masala-260', 'jild11-masala-261', 'jild11-masala-262', 'jild11-masala-263', 'jild11-masala-264', 'jild11-masala-265', 'jild11-masala-266', 'jild11-masala-267', 'jild11-masala-268', 'jild11-masala-269', 'jild11-masala-270', 'jild11-masala-271', 'jild11-masala-272', 'jild11-masala-273', 'jild11-masala-274-276', 'jild11-masala-277', 'jild11-masala-278', 'jild11-masala-279', 'jild11-p489', 'jild11-masala-280', 'jild11-masala-281', 'jild11-masala-282-284', 'jild11-masala-285-286', 'jild11-masala-287', 'jild11-masala-288', 'jild11-masala-289', 'jild11-masala-290', 'jild11-masala-291', 'jild11-masala-292-293', 'jild11-masala-294', 'jild11-masala-295', 'jild11-masala-296', 'jild11-masala-297', 'jild11-masala-298-300', 'jild11-masala-301', 'jild11-masala-302', 'jild11-masala-304', 'jild11-masala-305', 'jild11-masala-306', 'jild11-bab-al-wali', 'jild11-p523', 'jild11-masala-307', 'jild11-masala-308', 'jild11-masala-309', 'jild11-masala-310', 'jild11-masala-311', 'jild11-masala-312', 'jild11-masala-313', 'jild11-masala-314', 'jild11-masala-315', 'jild11-masala-316', 'jild11-masala-317', 'jild11-masala-318', 'jild11-masala-319', 'jild11-masala-320', 'jild11-masala-321', 'jild11-masala-322', 'jild11-masala-323', 'jild11-masala-324', 'jild11-masala-325', 'jild11-masala-326', 'jild11-masala-327', 'jild11-masala-328', 'jild11-masala-329', 'jild11-masala-330', 'jild11-masala-331', 'jild11-masala-332', 'jild11-masala-333', 'jild11-masala-334', 'jild11-masala-335', 'jild11-masala-336', 'jild11-masala-337', 'jild11-risala-tajweez', 'jild11-masala-338', 'jild11-masala-339', 'jild11-masala-340', 'jild11-masala-341', 'jild11-masala-342', 'jild11-p609', 'jild11-masala-343', 'jild11-masala-344', 'jild11-masala-345', 'jild11-masala-346', 'jild11-masala-347', 'jild11-p620', 'jild11-masala-349', 'jild11-masala-350', 'jild11-masala-351', 'jild11-masala-352', 'jild11-masala-353', 'jild11-masala-354', 'jild11-masala-355', 'jild11-masala-356', 'jild11-masala-357', 'jild11-masala-358', 'jild11-masala-359-366', 'jild11-masala-367', 'jild11-masala-368', 'jild11-masala-369', 'jild11-masala-370', 'jild11-masala-371', 'jild11-masala-372', 'jild11-masala-373', 'jild11-masala-374', 'jild11-masala-375', 'jild11-masala-376-377', 'jild11-masala-378', 'jild11-masala-379', 'jild11-masala-380', 'jild11-masala-381', 'jild11-masala-382', 'jild11-masala-383-390', 'jild11-masala-391', 'jild11-masala-392', 'jild11-masala-393', 'jild11-masala-394', 'jild11-masala-395', 'jild11-masala-396', 'jild11-masala-397', 'jild11-masala-398', 'jild11-masala-399', 'jild11-masala-400', 'jild11-masala-401', 'jild11-masala-405', 'jild11-masala-407', 'jild11-masala-408', 'jild11-masala-409', 'jild11-masala-410', 'jild11-masala-411', 'jild11-masala-413', 'jild11-masala-414', 'jild11-masala-415', 'jild11-masala-416', 'jild11-masala-417', 'jild11-masala-418', 'jild11-masala-419', 'jild11-masala-420', 'jild11-masala-421', 'jild11-p686', 'jild11-masala-423', 'jild11-masala-424', 'jild11-masala-425', 'jild11-masala-426', 'jild11-masala-427', 'jild11-masala-428', 'jild11-p691', 'jild11-masala-429', 'jild11-masala-430', 'jild11-masala-431', 'jild11-masala-432', 'jild11-masala-433', 'jild11-masala-434', 'jild11-masala-435', 'jild11-masala-436', 'jild11-masala-437', 'jild11-masala-438', 'jild11-masala-439', 'jild11-masala-440', 'jild11-masala-441', 'jild11-masala-442', 'jild11-masala-443-446', 'jild11-masala-447', 'jild11-masala-448', 'jild11-masala-449', 'jild11-masala-450', 'jild11-masala-451', 'jild11-masala-452-454', 'jild11-masala-455', 'jild11-masala-456', 'jild11-masala-457', 'jild11-masala-458', 'jild11-masala-459']

# v3 pages per item id, verbatim from content/tashreeh/jild-11.json.
V3_PAGES = {
"jild11-pesh-lafz": [6, 7],
"jild11-masala-1": [110, 111],
"jild11-masala-2": [111, 112, 113, 114, 115, 116, 117, 118],
"jild11-masala-3": [118],
"jild11-masala-4": [119, 120],
"jild11-masala-5-6": [122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141],
"jild11-p142": [142],
"jild11-masala-7": [142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155],
"jild11-masala-8": [155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172],
"jild11-masala-9": [172, 173, 174],
"jild11-masala-10": [174, 175, 176, 177, 178, 179, 180, 181],
"jild11-masala-11": [181],
"jild11-masala-12": [181, 182],
"jild11-masala-13": [182, 183, 184, 185, 186, 187, 188],
"jild11-masala-14-15": [189, 190, 191],
"jild11-masala-16": [191, 192],
"jild11-masala-17": [193],
"jild11-masala-18": [193, 194, 195],
"jild11-masala-19": [195, 196],
"jild11-masala-20": [196, 197],
"jild11-masala-21": [197, 198, 199, 200, 201],
"jild11-masala-22": [201, 202, 203, 204, 205, 206, 207],
"jild11-masala-23": [207, 208],
"jild11-masala-24": [208],
"jild11-masala-25": [208, 209],
"jild11-masala-26": [209, 210],
"jild11-masala-27": [210, 211, 212, 213, 214],
"jild11-masala-28": [214],
"jild11-masala-29": [214, 215],
"jild11-masala-30": [215, 216],
"jild11-masala-31": [216, 217],
"jild11-masala-32": [217, 218],
"jild11-masala-33": [218, 219],
"jild11-masala-34": [219, 220],
"jild11-masala-35": [220],
"jild11-masala-36": [220, 221],
"jild11-masala-37": [221, 222, 223],
"jild11-masala-38": [223],
"jild11-masala-39": [223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236],
"jild11-masala-40": [236, 237],
"jild11-masala-41": [237],
"jild11-masala-42": [238],
"jild11-masala-43-44": [238, 239],
"jild11-masala-45": [239, 240],
"jild11-masala-46": [240, 241, 242],
"jild11-masala-47": [242, 243],
"jild11-masala-48": [243],
"jild11-masala-49": [243, 244],
"jild11-masala-50": [244, 245],
"jild11-masala-51": [245, 246],
"jild11-masala-53": [246],
"jild11-masala-54": [247],
"jild11-masala-55": [247, 248],
"jild11-masala-56": [248],
"jild11-masala-57": [248],
"jild11-masala-58": [248, 249],
"jild11-masala-59": [249, 250],
"jild11-masala-60": [250, 251],
"jild11-masala-61": [251, 252, 253],
"jild11-masala-62": [253],
"jild11-masala-63": [254],
"jild11-masala-64": [254, 255],
"jild11-masala-65": [255],
"jild11-masala-66": [256, 257],
"jild11-masala-73": [257],
"jild11-masala-74": [258],
"jild11-masala-75": [258],
"jild11-masala-76": [259],
"jild11-masala-77": [259],
"jild11-masala-78": [260],
"jild11-masala-79": [260],
"jild11-masala-81": [261, 262],
"jild11-masala-82": [262],
"jild11-masala-83": [262],
"jild11-masala-84": [262, 263],
"jild11-masala-85": [263, 264],
"jild11-masala-87": [265],
"jild11-masala-88": [265, 266],
"jild11-masala-89": [266],
"jild11-masala-90": [266],
"jild11-masala-92": [267],
"jild11-masala-93": [267, 268],
"jild11-masala-94": [268],
"jild11-masala-95": [268, 269],
"jild11-masala-96": [269],
"jild11-masala-97": [269, 270],
"jild11-masala-98": [270, 271],
"jild11-masala-99": [271],
"jild11-masala-100": [272],
"jild11-masala-101": [272],
"jild11-masala-102": [272, 273],
"jild11-masala-103": [273, 274],
"jild11-masala-104": [275],
"jild11-p275": [275, 276],
"jild11-masala-107": [276, 277],
"jild11-masala-108": [277, 278],
"jild11-masala-109": [278, 279],
"jild11-masala-112": [279],
"jild11-masala-113": [279, 280],
"jild11-masala-114": [280],
"jild11-masala-115": [280, 281],
"jild11-masala-117": [281, 282],
"jild11-masala-118": [282],
"jild11-masala-119": [282, 283],
"jild11-masala-120": [283, 284],
"jild11-masala-121": [285, 286],
"jild11-masala-122": [286, 287],
"jild11-masala-128": [287, 288],
"jild11-masala-129": [288],
"jild11-masala-130": [288],
"jild11-masala-131": [288, 289],
"jild11-masala-132": [289, 290],
"jild11-masala-133": [290, 291],
"jild11-masala-135": [291, 292],
"jild11-masala-136": [292, 293],
"jild11-masala-137": [294],
"jild11-masala-138": [294, 295],
"jild11-masala-139": [295, 296],
"jild11-masala-140": [296],
"jild11-masala-141": [296, 297],
"jild11-masala-142": [297, 298],
"jild11-masala-143": [298],
"jild11-masala-144-147": [298, 299, 300],
"jild11-masala-148": [300, 302],
"jild11-masala-149": [302],
"jild11-masala-150": [303, 304, 305],
"jild11-masala-152": [305, 306, 307],
"jild11-masala-153": [307, 308, 309, 310, 311],
"jild11-masala-154": [311],
"jild11-p313": [313],
"jild11-masala-155": [313, 314],
"jild11-masala-156": [314],
"jild11-masala-157": [314, 315, 316],
"jild11-masala-158": [316, 317],
"jild11-masala-159": [317],
"jild11-masala-160": [317, 318],
"jild11-masala-161": [318],
"jild11-masala-162": [318, 319],
"jild11-masala-163": [319, 320],
"jild11-masala-164": [320, 321, 322, 323, 324],
"jild11-masala-165": [324, 325],
"jild11-masala-166": [325, 326],
"jild11-masala-167": [326, 327],
"jild11-masala-168": [327, 328, 329, 330],
"jild11-masala-169": [330, 331],
"jild11-masala-170": [331],
"jild11-masala-171": [331, 332],
"jild11-masala-172": [332, 333],
"jild11-masala-173": [333, 334],
"jild11-masala-174": [334],
"jild11-masala-175": [334, 335],
"jild11-masala-176-177": [335, 336, 337, 338, 339, 340],
"jild11-masala-178": [340, 341],
"jild11-masala-179": [341],
"jild11-masala-180": [341],
"jild11-masala-181": [341, 342],
"jild11-masala-182": [342],
"jild11-masala-183": [342, 343, 344],
"jild11-masala-184": [344, 345],
"jild11-masala-185": [345],
"jild11-masala-186-188": [345, 346],
"jild11-masala-189": [346, 347],
"jild11-masala-190": [347, 348],
"jild11-masala-191": [348, 349],
"jild11-masala-192": [349, 350, 351],
"jild11-masala-193": [351, 352, 353],
"jild11-masala-194": [353],
"jild11-masala-195": [355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368],
"jild11-masala-196": [368, 369],
"jild11-masala-197": [369, 370, 371, 372],
"jild11-masala-198": [372, 373],
"jild11-masala-199": [375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407],
"jild11-masala-200": [407, 408],
"jild11-masala-201": [408, 409, 410, 411],
"jild11-masala-202": [412],
"jild11-masala-203": [412, 413, 414],
"jild11-masala-204": [414, 415],
"jild11-masala-205": [415, 416],
"jild11-masala-209": [416, 417],
"jild11-masala-210": [417, 418, 419],
"jild11-masala-211": [419, 420, 421, 422, 423],
"jild11-masala-213": [423, 424],
"jild11-masala-214": [424],
"jild11-masala-215": [424, 425],
"jild11-masala-216": [425],
"jild11-masala-217": [425, 426],
"jild11-masala-218": [426, 427],
"jild11-masala-219": [427, 428],
"jild11-masala-220": [428, 429],
"jild11-masala-221": [429, 430],
"jild11-masala-222": [431, 432],
"jild11-masala-223": [432, 433, 434, 435, 436, 437],
"jild11-masala-227": [437, 438],
"jild11-masala-228": [438, 439],
"jild11-masala-229": [439, 440],
"jild11-masala-232": [440, 441],
"jild11-masala-234": [441],
"jild11-masala-235": [441, 442, 443],
"jild11-masala-236": [443, 444, 445],
"jild11-masala-237": [445, 446, 447],
"jild11-masala-238": [447],
"jild11-masala-239": [447, 448],
"jild11-masala-240": [448, 449],
"jild11-masala-241": [449, 450],
"jild11-masala-242": [450],
"jild11-masala-243": [450, 451, 452, 453],
"jild11-masala-244": [453],
"jild11-masala-245": [453, 454],
"jild11-masala-246": [454, 455],
"jild11-masala-247": [455],
"jild11-masala-248": [455, 456],
"jild11-masala-249": [456],
"jild11-masala-250": [456],
"jild11-masala-251": [456, 457],
"jild11-masala-252": [457],
"jild11-masala-253": [457, 458],
"jild11-masala-254": [458],
"jild11-masala-255": [458, 459],
"jild11-masala-256": [459, 460],
"jild11-masala-257": [460, 461, 462],
"jild11-masala-258": [462, 463],
"jild11-masala-259": [462, 463],
"jild11-masala-260": [463],
"jild11-masala-261": [463, 464],
"jild11-masala-262": [464],
"jild11-masala-263": [465],
"jild11-masala-264": [465],
"jild11-masala-265": [465, 466],
"jild11-masala-266": [466, 467],
"jild11-masala-267": [467],
"jild11-masala-268": [467, 468],
"jild11-masala-269": [467, 468],
"jild11-masala-270": [468],
"jild11-masala-271": [468, 469],
"jild11-masala-272": [469],
"jild11-masala-273": [469],
"jild11-masala-274-276": [470, 471],
"jild11-masala-277": [471],
"jild11-masala-278": [471],
"jild11-masala-279": [471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488],
"jild11-p489": [489, 490],
"jild11-masala-280": [490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507],
"jild11-masala-281": [507, 508],
"jild11-masala-282-284": [507, 508],
"jild11-masala-285-286": [508],
"jild11-masala-287": [508, 509],
"jild11-masala-288": [509, 510],
"jild11-masala-289": [510, 511],
"jild11-masala-290": [511],
"jild11-masala-291": [511, 512],
"jild11-masala-292-293": [512],
"jild11-masala-294": [512],
"jild11-masala-295": [512, 513, 514],
"jild11-masala-296": [514, 515],
"jild11-masala-297": [515, 516],
"jild11-masala-298-300": [516, 517, 518],
"jild11-masala-301": [518, 519],
"jild11-masala-302": [519, 520],
"jild11-masala-304": [520, 521],
"jild11-masala-305": [521],
"jild11-masala-306": [521, 522],
"jild11-bab-al-wali": [523],
"jild11-p523": [523, 524, 525],
"jild11-masala-307": [526],
"jild11-masala-308": [526, 527, 528, 529, 530],
"jild11-masala-309": [530, 531],
"jild11-masala-310": [531, 532],
"jild11-masala-311": [532, 533, 534],
"jild11-masala-312": [534, 535],
"jild11-masala-313": [535, 536, 537, 538, 539, 540],
"jild11-masala-314": [540, 541, 542, 543],
"jild11-masala-315": [543, 544],
"jild11-masala-316": [544, 545, 546],
"jild11-masala-317": [546],
"jild11-masala-318": [546, 547],
"jild11-masala-319": [547],
"jild11-masala-320": [547, 548, 549],
"jild11-masala-321": [549, 550, 551, 552],
"jild11-masala-322": [552, 553],
"jild11-masala-323": [553, 554],
"jild11-masala-324": [555, 556],
"jild11-masala-325": [556, 557, 558, 559],
"jild11-masala-326": [559, 560],
"jild11-masala-327": [561],
"jild11-masala-328": [561, 562, 563, 564, 565],
"jild11-masala-329": [565, 566],
"jild11-masala-330": [566, 567],
"jild11-masala-331": [567, 568],
"jild11-masala-332": [568, 569, 570, 571, 572],
"jild11-masala-333": [572, 573],
"jild11-masala-334": [573, 574, 575, 576, 577, 578, 579, 580],
"jild11-masala-335": [580, 581, 582, 583],
"jild11-masala-336": [583, 584, 585],
"jild11-masala-337": [585, 586],
"jild11-risala-tajweez": [587],
"jild11-masala-338": [587],
"jild11-masala-339": [588, 589, 590, 591, 592],
"jild11-masala-340": [592, 593, 594],
"jild11-masala-341": [594, 595, 596, 597, 598, 599],
"jild11-masala-342": [599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609],
"jild11-p609": [609, 610, 611],
"jild11-masala-343": [611, 612],
"jild11-masala-344": [612, 613, 614],
"jild11-masala-345": [614, 615],
"jild11-masala-346": [615, 616],
"jild11-masala-347": [616, 617, 618, 619],
"jild11-p620": [620, 621],
"jild11-masala-349": [620, 621, 622],
"jild11-masala-350": [622, 623],
"jild11-masala-351": [623, 624, 626],
"jild11-masala-352": [626, 627],
"jild11-masala-353": [627, 628],
"jild11-masala-354": [628],
"jild11-masala-355": [628, 629],
"jild11-masala-356": [629, 630],
"jild11-masala-357": [630, 631, 632],
"jild11-masala-358": [632, 633],
"jild11-masala-359-366": [633, 634, 635, 636],
"jild11-masala-367": [636, 637],
"jild11-masala-368": [637, 638, 639],
"jild11-masala-369": [639, 640],
"jild11-masala-370": [640],
"jild11-masala-371": [640, 641],
"jild11-masala-372": [641, 642, 643, 644],
"jild11-masala-373": [644, 645],
"jild11-masala-374": [645, 646, 647],
"jild11-masala-375": [647, 648],
"jild11-masala-376-377": [648, 649, 650],
"jild11-masala-378": [650, 651],
"jild11-masala-379": [651],
"jild11-masala-380": [651, 652],
"jild11-masala-381": [652, 653],
"jild11-masala-382": [653, 654],
"jild11-masala-383-390": [654, 655, 656],
"jild11-masala-391": [656, 657],
"jild11-masala-392": [657, 658],
"jild11-masala-393": [658],
"jild11-masala-394": [658, 659, 660, 661, 662, 663],
"jild11-masala-395": [663, 664],
"jild11-masala-396": [664, 665],
"jild11-masala-397": [665],
"jild11-masala-398": [665, 666],
"jild11-masala-399": [666, 667, 668, 669],
"jild11-masala-400": [669, 670],
"jild11-masala-401": [670, 671],
"jild11-masala-405": [670, 671, 672],
"jild11-masala-407": [672, 673],
"jild11-masala-408": [673, 674],
"jild11-masala-409": [674, 675],
"jild11-masala-410": [675, 676],
"jild11-masala-411": [676],
"jild11-masala-413": [677],
"jild11-masala-414": [677, 678],
"jild11-masala-415": [678, 679],
"jild11-masala-416": [679, 680],
"jild11-masala-417": [680, 681],
"jild11-masala-418": [681, 682],
"jild11-masala-419": [682, 683],
"jild11-masala-420": [683, 684],
"jild11-masala-421": [684, 685],
"jild11-p686": [686],
"jild11-masala-423": [686, 687],
"jild11-masala-424": [686, 687],
"jild11-masala-425": [687],
"jild11-masala-426": [687, 688],
"jild11-masala-427": [688, 689],
"jild11-masala-428": [689, 690],
"jild11-p691": [691],
"jild11-masala-429": [691, 692, 693],
"jild11-masala-430": [693, 694, 695, 696, 697, 698, 699],
"jild11-masala-431": [699, 700],
"jild11-masala-432": [700, 701, 702, 703],
"jild11-masala-433": [703, 704],
"jild11-masala-434": [704, 705],
"jild11-masala-435": [705, 706, 707],
"jild11-masala-436": [707],
"jild11-masala-437": [707, 708, 709, 710, 711, 712, 713],
"jild11-masala-438": [713, 714],
"jild11-masala-439": [715, 716, 717, 718, 719],
"jild11-masala-440": [719],
"jild11-masala-441": [719, 720],
"jild11-masala-442": [720, 721],
"jild11-masala-443-446": [721, 722, 723, 724, 725],
"jild11-masala-447": [725, 726, 727, 728],
"jild11-masala-448": [728, 729, 730, 731],
"jild11-masala-449": [731],
"jild11-masala-450": [731, 732],
"jild11-masala-451": [732, 733],
"jild11-masala-452-454": [733],
"jild11-masala-455": [733, 734],
"jild11-masala-456": [734, 735],
"jild11-masala-457": [735, 736],
"jild11-masala-458": [736, 737],
"jild11-masala-459": [737, 738, 739],
}

# The Urdu word for "page" is safha; the canonical marker is [safha N].
# Lenticular brackets are U+3010 (open) and U+3011 (close); the short
# form is "[safha-initial N]" with the single-letter abbreviation.
# All three patterns are built from escapes so this file never contains
# a literal lenticular-bracket pair.
SAFHA = "\u0635\u0641\u062d\u06c1"  # the Urdu word for page
RE_LENTICULAR = re.compile("\u3010" + SAFHA + " (\\d+)\u3011")
RE_SHORT = re.compile("\\[\u0635 (\\d+)\\]")
RE_FULL = re.compile("\\[" + SAFHA + " \\d+\\]")
LENTICULAR_PREFIX = "\u3010" + SAFHA  # for the "none remain" check
SHORT_PREFIX_RE = re.compile("\\[\u0635 \\d+\\]")

# Canonical output key order for every item (the JSON contract).
ITEM_KEYS = ["id", "title", "volume_id", "pages", "start_page",
             "tashreeh_sawal", "tashreeh_jawab", "notes"]


def normalise_markers(text):
    """Normalise page markers in one string. Returns (new_text, counts)."""
    counts = {"lenticular": 0, "short": 0, "full_before": 0}
    counts["full_before"] = len(RE_FULL.findall(text))
    text, n1 = RE_LENTICULAR.subn("[" + SAFHA + " \\1]", text)
    counts["lenticular"] = n1
    text, n2 = RE_SHORT.subn("[" + SAFHA + " \\1]", text)
    counts["short"] = n2
    return text, counts


def normalise_item(item):
    """Normalise markers in every string field of one item (recursively
    through lists/dicts). Returns per-form counts for this item."""
    totals = {"lenticular": 0, "short": 0, "full_before": 0}

    def walk(value):
        if isinstance(value, str):
            new, c = normalise_markers(value)
            for k in totals:
                totals[k] += c[k]
            return new
        if isinstance(value, list):
            return [walk(v) for v in value]
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        return value

    for key in list(item.keys()):
        item[key] = walk(item[key])
    return totals


def main():
    assert len(V3_IDS) == EXPECTED_ITEMS, "embedded V3_IDS length mismatch"
    assert set(V3_PAGES) == set(V3_IDS), "embedded V3_PAGES keys != V3_IDS"
    assert sum(len(v) for v in V3_PAGES.values()) >= EXPECTED_PAGES

    manifest = json.load(open(os.path.join(BASE, MANIFEST), encoding="utf-8"))
    entries = manifest["chunks"]
    assert len(entries) == 15, f"expected 15 manifest entries, got {len(entries)}"
    assert all(e.get("status") == "done" for e in entries), "not all chunks done"
    by_file = {e["file"]: e for e in entries}
    assert set(by_file) == set(CHUNK_ORDER), (
        f"manifest files != CHUNK_ORDER: "
        f"missing={set(CHUNK_ORDER) - set(by_file)} "
        f"extra={set(by_file) - set(CHUNK_ORDER)}"
    )

    all_items = []
    derived = []
    for fname in CHUNK_ORDER:
        path = os.path.join(BASE, fname)
        d = json.load(open(path, encoding="utf-8"))
        items = d["masail"]
        entry = by_file[fname]
        assert len(items) == entry["items"], (
            f"{fname}: {len(items)} items, manifest says {entry['items']}"
        )
        # Marker normalisation, with before/after counts per chunk.
        before = {"lenticular": 0, "short": 0, "full_before": 0}
        for it in items:
            c = normalise_item(it)
            for k in before:
                before[k] += c[k]
        after_full = sum(
            len(RE_FULL.findall(json.dumps(it, ensure_ascii=False)))
            for it in items
        )
        print(
            f"{fname}: {len(items)} items | markers before: "
            f"lenticular={before['lenticular']} short={before['short']} "
            f"full={before['full_before']} | after: full={after_full}"
        )
        assert after_full == (
            before["lenticular"] + before["short"] + before["full_before"]
        ), f"{fname}: marker count changed by normalisation!"
        # Derive start_page = min(pages) where absent (none expected: all chunks carry start_page).
        for it in items:
            if "start_page" not in it:
                it["start_page"] = min(it["pages"])
                derived.append(it["id"])
        all_items.extend(items)

    # NO RENAME QUIRK in Jild 11: the v3 merged file has 394 UNIQUE
    # ids — the book numbers no masala twice in this jild. Chunk ids
    # are used exactly as written.
    assert len(all_items) == len({it["id"] for it in all_items}), (
        f"DUPLICATE IDS before validation: "
        f"{[i for i in [it['id'] for it in all_items] if [it['id'] for it in all_items].count(i) > 1]}"
    )
    print("renames applied: [] (no duplicate masala numbers in Jild 11)")

    print(f"concatenated: {len(all_items)} items")
    print(f"start_page derived for {len(derived)} items (expected 0: all chunks carry start_page)")
    assert len(all_items) == EXPECTED_ITEMS, (
        f"expected {EXPECTED_ITEMS} items, got {len(all_items)}"
    )

    # Rebuild each item in the canonical key order (the JSON contract).
    canonical = []
    for it in all_items:
        assert set(it.keys()) == set(ITEM_KEYS), (
            f"{it.get('id')}: keys {sorted(it.keys())} != {sorted(ITEM_KEYS)}"
        )
        canonical.append({k: it[k] for k in ITEM_KEYS})
    all_items = canonical

    # Validation.
    ids = [it["id"] for it in all_items]
    assert ids == V3_IDS, (
        f"ID sequence != v3: first diff at "
        f"{next((i for i, (a, b) in enumerate(zip(ids, V3_IDS)) if a != b), min(len(ids), len(V3_IDS)))}"
    )
    assert len(ids) == len(set(ids)), (
        f"DUPLICATE IDS: {[i for i in ids if ids.count(i) > 1]}"
    )
    empty = [it["id"] for it in all_items if not it.get("tashreeh_jawab")]
    assert not empty, f"EMPTY JAWAB: {empty}"
    vols = set(it.get("volume_id") for it in all_items)
    assert vols == EXPECTED_VOLUME_IDS, f"volume_ids {vols} != {EXPECTED_VOLUME_IDS}"
    pages = set()
    for it in all_items:
        assert it["pages"] == V3_PAGES[it["id"]], (
            f"{it['id']}: pages {it['pages']} != v3 {V3_PAGES[it['id']]}"
        )
        pages.update(it["pages"])
    assert len(pages) == EXPECTED_PAGES, (
        f"expected {EXPECTED_PAGES} unique pages, got {len(pages)}"
    )
    assert min(pages) == EXPECTED_MIN_PAGE, f"min page {min(pages)}"
    assert max(pages) == EXPECTED_MAX_PAGE, f"max page {max(pages)}"
    exceptions = {
        it["id"] for it in all_items if it["start_page"] != min(it["pages"])
    }
    assert not exceptions, f"start_page != min(pages): {sorted(exceptions)}"
    assert ids[0] == EXPECTED_FIRST_ID, f"first id {ids[0]}"
    assert ids[-1] == EXPECTED_LAST_ID, f"last id {ids[-1]}"

    out = {"masail": all_items}
    out_text = json.dumps(out, ensure_ascii=False, indent=1)
    assert LENTICULAR_PREFIX not in out_text, "lenticular markers remain in output!"
    assert not SHORT_PREFIX_RE.search(out_text), "short markers remain in output!"
    total_markers = len(RE_FULL.findall(out_text))
    print(
        f"VALIDATION PASSED: {len(all_items)} items, {len(pages)} unique pages "
        f"(min {min(pages)}, max {max(pages)}), volume_ids {sorted(vols)}, "
        f"first {ids[0]}, last {ids[-1]}, start_page == min(pages) for all, "
        f"derived start_page for {len(derived)} items, markers {total_markers}"
    )

    with open(os.path.join(BASE, "jild-11.json"), "w", encoding="utf-8") as f:
        f.write(out_text)
    print(f"WROTE jild-11.json: {len(out_text.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
