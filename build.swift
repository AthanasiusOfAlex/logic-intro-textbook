#!/usr/bin/env xcrun swift

import Foundation

func getCommandPath(forCommand command: String) -> URL? {
    let task = Process()
    task.executableURL = URL(fileURLWithPath: "/usr/bin/which")
    task.arguments = [command]
    let outputPipe = Pipe()
    task.standardOutput = outputPipe
    
    do {
        try task.run()
        task.waitUntilExit()
    } catch {
        return nil
    }
    
    let outputData = outputPipe.fileHandleForReading.readDataToEndOfFile()
    let output = String(decoding: outputData, as: UTF8.self)
    let lines = output.split(separator: "\n")
    
    if lines.count<1 {
        return nil
    } else {
        return URL(fileURLWithPath: String(lines[0]))
    }
}

let fileManager = FileManager.default
let currentWorkingURL = URL(fileURLWithPath: fileManager.currentDirectoryPath, isDirectory: true)

let outputDirectoryName = "pdf"
let outputDirectoryURL = currentWorkingURL.appendingPathComponent(outputDirectoryName)

do {
    if !fileManager.fileExists(atPath: outputDirectoryURL.path) {
        try fileManager.createDirectory(at: outputDirectoryURL, withIntermediateDirectories: false, attributes: nil)
    }
} catch {
    print("Unable to create directory")
    exit(1)
}

do {
    let files = try fileManager.contentsOfDirectory(atPath: currentWorkingURL.path).filter{ file in
        file.hasSuffix("md")
    }

    for file in files {
        let task = Process()
        task.currentDirectoryURL = currentWorkingURL
        
        guard let executableURL = getCommandPath(forCommand: "md2pdf") else {
            print("unable to find md2pdf")
            exit(1)
        }
        
        let inputFileURL = currentWorkingURL.appendingPathComponent(file)
        let inputArgument = inputFileURL.path
        
        task.executableURL = executableURL
        let outputFileURL = outputDirectoryURL.appendingPathComponent(file)
        let outputArgument = outputFileURL.deletingPathExtension().path
        
        // md2pdf name.md -o pdfPath/name.pdf
        task.arguments = [inputArgument, "-o", outputArgument, "-t", "/Users/louismelahn/templates/logic-textbook.latex"]
        do {
            try task.run()
            task.waitUntilExit()
        } catch {
            print("unable to run task")
            exit(1)
        }
    }
} catch {
    print("Unable to list contents of directory")
    exit(1)
}
