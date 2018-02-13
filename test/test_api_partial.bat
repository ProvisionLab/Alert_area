@echo off
python -m unittest test_api.Test_auth
rem python -m unittest test_api.Test_get_cameras.test_1
rem python -m unittest test_api.Test_get_cameras.test_bad_auth
rem python -m unittest test_api.Test_get_camera.test_1
rem python -m unittest test_api.Test_unknown_resource.test_1
rem python -m unittest test_api.Test_get_camera.test_unknown_camera_1
rem python -m unittest test_api.Test_get_camera.test_unknown_camera_2
rem python -m unittest test_api.Test_camera_alerts
rem python -m unittest test_api.Test_camera_alerts.test_get_1
rem python -m unittest test_api.Test_camera_alerts.test_post_1
rem python -m unittest test_api.Test_camera_alerts.test_delete_1
