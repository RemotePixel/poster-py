
from setuptools import setup

# Parse the version from the poster module.
with open('poster/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue


setup(name='poster',
      version=version,
      python_requires='>=3',
      description=u"do the job",
      long_description=u"do my job",
      author=u"Vincent Sarago",
      author_email='contact@remotepixel.ca',
      license='BSD',
      packages=['poster'],
      package_data={'assets': ['*.png']},
      include_package_data=True,
      install_requires=[
        'Pillow',
        'numpy',
        'click',
        'rasterio[s3]>=1.0a11',
        'Wand'
      ],
      zip_safe=False,
      entry_points={
          'console_scripts': [
            'poster = poster.cli.cli:create'
          ]
      })
