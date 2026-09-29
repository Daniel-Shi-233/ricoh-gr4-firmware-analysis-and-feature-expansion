import Foundation
import ImageCaptureCore

final class CameraProbe: NSObject, ICDeviceBrowserDelegate, ICDeviceDelegate {
    let browser = ICDeviceBrowser()
    var camera: ICCameraDevice?

    func start() {
        browser.delegate = self
        browser.start()
        RunLoop.current.run(until: Date().addingTimeInterval(12))
        camera?.requestCloseSession()
        browser.stop()
    }

    func deviceBrowser(_ browser: ICDeviceBrowser, didAdd device: ICDevice, moreComing: Bool) {
        print("Device: \(device.name ?? "unknown"), type=\(device.type.rawValue), transport=\(device.transportType ?? "unknown")")
        guard device.name?.contains("GR IV") == true, let camera = device as? ICCameraDevice else { return }
        self.camera = camera
        camera.delegate = self
        camera.requestOpenSession()
    }

    func deviceBrowser(_ browser: ICDeviceBrowser, didRemove device: ICDevice, moreGoing: Bool) {
        print("Removed: \(device.name ?? "unknown")")
    }

    func device(_ device: ICDevice, didOpenSessionWithError error: Error?) {
        if let error { print("Open session error: \(error)"); return }
        guard let camera = device as? ICCameraDevice else { return }
        print("Session open. Capabilities: \(camera.capabilities ?? [])")
        print("Locked: \(camera.isLocked), catalog: \(camera.contentCatalogPercentCompleted)%")
        print("Top-level contents: \(camera.contents?.count ?? 0)")
        for item in camera.contents ?? [] {
            print("  \(item.name ?? "unknown") / \(type(of: item))")
        }
    }

    func device(_ device: ICDevice, didCloseSessionWithError error: Error?) {
        print("Session closed: \(String(describing: error))")
    }
}

CameraProbe().start()
