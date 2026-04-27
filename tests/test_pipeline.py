"""Unit tests for pipeline internals (no model loading)."""

from pipeline.cluster import ClusterTracker
from pipeline.nms import _iou, _same_family, cross_class_nms


def test_iou_no_overlap():
    assert _iou([0, 0, 10, 10], [20, 20, 30, 30]) == 0.0


def test_iou_full_overlap():
    box = [0.0, 0.0, 10.0, 10.0]
    assert abs(_iou(box, box) - 1.0) < 1e-5


def test_iou_partial():
    iou = _iou([0, 0, 10, 10], [5, 0, 15, 10])
    assert 0.3 < iou < 0.4


def test_same_family_true():
    assert _same_family("soapbar_dove_shea", "soapbar_dove_lavender")


def test_same_family_false():
    assert not _same_family("soapbar_dove_shea", "milk_delice")


def test_cross_class_nms_suppresses_overlap():
    dets = [
        [0, 0, 100, 100, 0.9, 0],
        [5, 5, 95, 95, 0.7, 1],
    ]
    result = cross_class_nms(dets, model_names={0: "milk_delice", 1: "juice_diva"})
    assert len(result) == 1
    assert result[0][4] == 0.9


def test_cross_class_nms_keeps_non_overlap():
    dets = [
        [0, 0, 50, 50, 0.9, 0],
        [200, 0, 250, 50, 0.8, 1],
    ]
    result = cross_class_nms(dets)
    assert len(result) == 2


def test_cluster_tracker_single_box():
    tracker = ClusterTracker(dist_threshold=80)
    result = tracker.update([[0, 0, 100, 100]])
    assert len(result) == 1
    cid, _ = result[0]
    assert cid == 0


def test_cluster_tracker_same_cluster():
    tracker = ClusterTracker(dist_threshold=80)
    tracker.update([[0, 0, 100, 100]])
    result = tracker.update([[5, 5, 105, 105]])
    assert result[0][0] == 0


def test_cluster_tracker_confirmed():
    tracker = ClusterTracker(dist_threshold=80)
    for _ in range(6):
        tracker.update([[0, 0, 100, 100]])
    assert tracker.confirmed_count(6) == 1
    assert tracker.any_confirmed(6)