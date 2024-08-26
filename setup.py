from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

class CustomInstallCommand(install):
    def run(self):
        # First, run the standard installation
        install.run(self)

        # Now handle the custom installation of other_directory
        self.move_other_directory()

    def move_other_directory(self):
        # Define the source and target paths
        source = os.path.join(os.path.dirname(__file__), 'lex', 'generic_app')
        target = os.path.join(os.path.dirname(self.install_lib), 'generic_app')

        # Ensure the package_data entry points to the correct location
        if os.path.exists(target):
            shutil.rmtree(target)  # Remove the existing directory if it exists
        shutil.move(source, target)
        print(f'Moved other_directory to {target}')

setup(
    name="lex-app",
    version="1.0.0",
    author="Melih Sünbül",
    author_email="m.sunbul@lund-it.com",
    description="A Python / Django library to create business applications easily with complex logic",
    long_description_content_type="text/markdown",
    url="https://github.com/LundIT/lex-app",
    packages=find_packages(),
    package_data={
        '': ['generic_app/*'],  # Track the moved directory for cleanup
    },
    cmdclass={
        'install': CustomInstallCommand,
    },

    include_package_data=True,
    entry_points={
        'console_scripts': [
            'lex = lex.__main__:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires,
    python_requires='>=3.6',
)
