## Submitting samples

### Developer Certificate of Origin

Before you start working with this project, please read our [Developer Certificate of Origin](https://cla.vmware.com/dco). All contributions to this repository must be signed as described on that page. Your signature certifies that you wrote the patch or have the right to pass it on as an open-source patch.

### Sample Template

[Sample template](sample_template) contains boilerplate code that can be used to build a new sample.
Please copy one of the files and use it as a starting point to write a new sample.

### Required Information

The following information must be included in the README.md or in the sample docstring in case README already exists in same folder.
* Author Name
  * This can include full name, email address or other identifiable piece of information that would allow interested parties to contact author with questions.
* Compatible vCenter version
  * This should be the vCenter version when the API is introduced, something like "6.5+" or "6.8.1+".
* Minimal/High Level Description
  * What does the sample do ?
* Any KNOWN limitations or dependencies

### Contribution Process

* Follow the [GitHub process](https://help.github.com/articles/fork-a-repo)
  * Please use one branch per sample or change-set
  * Please use one commit and pull request per sample
  * Please post the sample output along with the pull request
  * If you include a license with your sample, use the project license

### Code Style

Please conform to pep8 standards: https://pypi.python.org/pypi/pep8 with exceptions listed in setup.cfg
