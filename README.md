# UpgradePipPkgs

> Tool for upgrading all global `pip` packages with one command.

---

## About

- **_`UpgradePipPkgs`_** can upgrade all of your `pip` packages using one of two methods:

  **Method 1:**

  > **First gather all outdated packages using the command `pip list --outdated`, then pass results to a list of outdated packages to be upgraded.**

  - This method is generally more efficient than the following method, as only outdated packages are passed to upgrade process.
  - Unfortunately doesn't take into account package dependencies relying on specific package versions to function properly.

  ---

  **Method 2:**

  > **Iterate over _all_ installed packages, passing the command `pip install --upgrade {pkgname}` over each one.**

  - This method takes more time overall, but is "safer".
  - "Safer" in this context meaning that package dependencies are corrected upon attempting upgrade on a package that specifies its dependencies, downgrading specific package versions where necessary.
  - Note that not all packages will be able to downgrade, as the order of packages upgraded is relevant to whether incorrect version dependencies are corrected.
    - For example, let's assume **`PackA`** requires **`PackB<=1.0.0`** as a dependency:
      1. **`PackA`** will be checked for available upgrade first, and will check for installed dependency pkg **`PackB<=1.0.0`**, installing it if not already installed.
      2. `PackB` is then checked, and has a new version available, `1.1.0`.
      3. `PackB-1.0.0` is then upgraded to `1.1.0`, but now `PackA` can't function correctly due to incorrect dependency version.
      4. This can easily be fixed by reinstalling `PackA` using the `pip` install command: "`pip install PackA`".

- You can review past results/program output in the application's log file, which can be found here:
  - `"~/UpgradePipPkgs/logs/output.log"`

---

## Installation

### Using PIP _(Recommended)_

> _Easiest_ method. Highly recommended over manual installation.

- To install _**`UpgradePipPkgs`**_ using `pip`, enter the following in your commandline environment:

  ```python
  > pip install UpgradePipPkgs
  ```

- You should now be able to import/run _**`UpgradePipPkgs`**_ within your python environment by entering the following:

  ```python
  >>> from UpgradePipPkgs import upgrade_pip_pkgs
  ...
  ```

- Done!

---

### Manual Installation

> _Not_ recommended.

1. Before use, navigate to intended installation location, and create a new directory.
2. Install all dependencies for this package within said directory using:

   ```python
     pip install -r requirements.txt
   ```

3. Clone repository with the git client of your preference.
   - (Optional) move installation directory to `"path/to/Python/Libs/site_packages"` to be able to import this package to a Python program like any other importable package.

- Done!

---

## Usage

- In order to use _**`UpgradePipPkgs`**_, start by importing the module to your Python environment:

  ```python
  >>> from UpgradePipPkgs import upgrade_pip_pkgs
  ```

- Call the `upgrade_pip_pkgs` function to start the application, and choose the method of operation by typing the option number, and press **[ENTER]**.

![alt](./img/README_screenshot.png)

---

## Contact the Author

- If you have any questions, comments, or concerns that cannot be alleviated through the [project's GitHub repository "issues" tab](https://github.com/schlopp96/UpgradePipPkgs), please feel free to contact me through my email address:
  - `schloppdaddy@gmail.com`

---
