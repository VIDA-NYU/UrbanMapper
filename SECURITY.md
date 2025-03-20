<div align="center">
   <h1>UrbanMapper</h1>
   <h3>Enrich Urban Layers Given Urban Datasets</h3>
   <p><i>with ease-of-use API and Sklearn-alike Shareable & Reproducible Urban Pipeline</i></p>
   <p>
      <img src="https://img.shields.io/static/v1?label=Beartype&message=compliant&color=4CAF50&style=for-the-badge&logo=https://avatars.githubusercontent.com/u/63089855?s=48&v=4&logoColor=white" alt="Beartype compliant">
      <img src="https://img.shields.io/static/v1?label=UV&message=compliant&color=2196F3&style=for-the-badge&logo=UV&logoColor=white" alt="UV compliant">
      <img src="https://img.shields.io/static/v1?label=RUFF&message=compliant&color=9C27B0&style=for-the-badge&logo=RUFF&logoColor=white" alt="RUFF compliant">
      <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter">
      <img src="https://img.shields.io/static/v1?label=Python&message=3.9%2B&color=3776AB&style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+">
   </p>
</div>

# Security Reporting

If you wish to report a security vulnerability but not in a public issue—thank you!—we ask that you follow the process
below.

Please report security vulnerabilities by filling out the following template:

- **PROJECT**: A URL to the project's repository (e.g., `https://github.com/VIDA-NYU/UrbanMapper`)
- **PUBLIC**: Please let us know if this vulnerability has been made or discussed publicly already, and if so, please
  let us know where.
- **DESCRIPTION**: Please provide a precise description of the security vulnerability you have found with as much
  information as you are able and willing to provide.

Please send the above information, along with any other details you feel are pertinent, to: **sgp28@kent.ac.uk**.

In addition, you may request that the project provide you a patched release in advance of the release announcement;
however, we cannot guarantee that such information will be provided to you before the public release and announcement.

However, **sgp28@kent.ac.uk** will email you at the same time the public announcement is made. We will let you know
within a few weeks whether or not your report has been accepted or rejected. We ask that you please keep the report
confidential until we have made a public announcement.

## Potential Security Issues in Data Libraries

UrbanMapper is a Python library designed to work with urban datasets, which may include sensitive information such as
geospatial data or personal identifiers. Below are some potential security issues that could affect data libraries like
UrbanMapper:

- **Data Breaches**: If unauthorized access occurs, sensitive data (e.g., addresses, location histories) could be
  exposed, potentially violating privacy laws or harming individuals whose data is compromised.
- **Insecure Data Handling**: Without proper encryption during storage or transmission, data could be intercepted or
  altered by malicious actors.
- **Injection Attacks**: If the library processes user inputs (e.g., file paths or queries) without proper sanitization,
  it could be vulnerable to attacks like SQL injection or command injection.
- **Dependency Vulnerabilities**: Relying on outdated or insecure third-party libraries could introduce exploitable
  weaknesses into UrbanMapper.
- **Geospatial Data Privacy**: Improper handling of location data—such as failing to anonymize or aggregate it—could
  reveal sensitive details about individuals or organizations.
- **Data Integrity Issues**: If data validation is insufficient, corrupted or malicious inputs could be processed,
  leading to unreliable outputs or flawed urban analyses.

To mitigate these risks, UrbanMapper prioritises secure coding, regular dependency updates, and comprehensive testing.
If you uncover any vulnerabilities, please report them following the steps mentioned above.
