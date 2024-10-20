# SportsHunt

**Version:** 0.1.0-beta

## Overview

A event mangement platform, tring to digitilize every part of sports industries.

## 3rd Party

- **User Authentication System:** Auth0.
- **Database :** Azure postges DB
- **Team Management:** Register teams, manage team details, and handle offline registrations.
- **Match Scheduling:** Automatically or manually schedule matches, including knockout fixtures.
- **Score Tracking:** Track match scores and update them in real-time.
- **Responsive Design:** Mobile-friendly design to ensure accessibility on various devices.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/sportshunt.git
    cd sportshunt
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up the database:
    ```sh
    python manage.py migrate
    ```

5. Run the development server:
    ```sh
    python manage.py runserver
    ```

## Configuration

Configuration settings can be found in the `sportshunt/conf/` directory. There are separate settings for development and production environments:
- Common: [sportshunt/conf/common.py](sportshunt/conf/common.py)
- Development: [sportshunt/conf/dev.py](sportshunt/conf/dev.py)
- Production: [sportshunt/conf/prod.py](sportshunt/conf/prod.py)

## Next Upgrades 

- Optimise the Code base.
- UI/UX total Redo
- Automatic KO fixture gen, RR, RR + KO



## License

SportsHunt is licensed under the GNU General Public License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any inquiries or support, please contact us at cto@sportshunt.in

---

