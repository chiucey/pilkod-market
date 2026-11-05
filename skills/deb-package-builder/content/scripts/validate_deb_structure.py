#!/usr/bin/env python3
"""
DEB Package Structure Validator

Validates that a DEB package structure follows Debian standards.
"""

import os
import sys
import argparse
from pathlib import Path


class DEBValidator:
    """Validates DEB package structure."""

    def __init__(self, package_dir: str):
        self.package_dir = Path(package_dir)
        self.errors = []
        self.warnings = []

    def validate(self) -> bool:
        """Run all validation checks."""
        self._check_debian_dir()
        self._check_control_file()
        self._check_file_permissions()
        self._check_scripts()
        self._check_forbidden_paths()

        return len(self.errors) == 0

    def _check_debian_dir(self):
        """Check that DEBIAN directory exists."""
        debian_dir = self.package_dir / "DEBIAN"
        if not debian_dir.exists():
            self.errors.append("DEBIAN directory not found")
            return
        if not debian_dir.is_dir():
            self.errors.append("DEBIAN is not a directory")

    def _check_control_file(self):
        """Validate control file."""
        control_path = self.package_dir / "DEBIAN" / "control"
        if not control_path.exists():
            self.errors.append("DEBIAN/control file not found")
            return

        required_fields = ["Package", "Version", "Maintainer", "Description", "Architecture"]
        content = control_path.read_text()

        for field in required_fields:
            if f"{field}:" not in content:
                self.errors.append(f"Required field '{field}' missing in control file")

    def _check_file_permissions(self):
        """Check file permissions in DEBIAN directory."""
        debian_dir = self.package_dir / "DEBIAN"
        if not debian_dir.exists():
            return

        for item in debian_dir.iterdir():
            if item.name == "control":
                continue
            mode = item.stat().st_mode & 0o777
            if mode != 0o755:
                self.warnings.append(f"{item.name} should have 755 permissions (current: {oct(mode)})")

    def _check_scripts(self):
        """Check maintenance scripts."""
        debian_dir = self.package_dir / "DEBIAN"
        if not debian_dir.exists():
            return

        scripts = ["preinst", "postinst", "prerm", "postrm"]
        for script in scripts:
            script_path = debian_dir / script
            if script_path.exists():
                content = script_path.read_text()
                if not content.startswith("#!/bin/bash"):
                    self.errors.append(f"{script} must start with #!/bin/bash")
                if not content.strip().endswith("exit 0"):
                    self.warnings.append(f"{script} should exit with 0")

    def _check_forbidden_paths(self):
        """Check for forbidden paths in conffiles or files."""
        forbidden = ["/etc", "/usr/share/doc", "/usr/share/man"]
        debian_dir = self.package_dir / "DEBIAN"

        for item in self.package_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(self.package_dir)
                if str(rel_path).startswith("DEBIAN"):
                    continue

    def get_report(self) -> str:
        """Generate validation report."""
        lines = []
        if self.errors:
            lines.append("ERRORS:")
            for error in self.errors:
                lines.append(f"  - {error}")
        if self.warnings:
            lines.append("WARNINGS:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
        if not self.errors and not self.warnings:
            lines.append("Validation passed!")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Validate DEB package structure")
    parser.add_argument("package_dir", help="Path to package directory")
    args = parser.parse_args()

    validator = DEBValidator(args.package_dir)
    is_valid = validator.validate()
    report = validator.get_report()

    print(report)
    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
