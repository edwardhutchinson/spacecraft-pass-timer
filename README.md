![Live Pass Example](/.img/live-pass.png)

# Spacecraft Pass Timer

The Spacecraft Pass Timer calculates a spacecraft's ground track and pass timings utilising two-line element (TLE) sets and user defined ground station locations. TLEs can be user inputted or searched for on [Celestrack](http://celestrak.com/NORAD/elements/) via spacecraft name. Right now, the application provides countdowns to all visibilities where spacecraft elevation, relative to a ground station, exceeds a defined angle.

## ⚡️ How to adjust tool for my mission?
1. Install requirements:
```
$ pip install -r requirements.txt
```
2. If using user defined TLE, update `/inputs/platform.tle` ensuring correct format is followed; see [Celestrak documentation](https://www.celestrak.com/NORAD/documentation/tle-fmt.php) for details. If searching for spacecraft on Celestrak, this step can be ignored.
3. Update `/inputs/ground_stations.json` file with to include all ground stations applicable to the mission.
4. *VISUAL ONLY* Update `/assets/logo.png` with mission spacecraft.

## ▶ Run tool

With inputs updated, run the Spacecraft Pass Timer tool from the command line:

```
Enter spacecraft name as defined in TLE set, leave blank for CRYOSAT 2...
->EXAMPLE SPACECRAFT
Provide path to TLE file, leave blank to search Celestrak...
->/inputs/platform.tle
Processing...
```
*Note: in the above example, a spacecraft titled 'EXAMPLE SPACECRAFT' should be included in the platform TLE file.* 

If happy using TLE definitions from Celestrak, input the spacecraft name and leave the second input blank.

These inputs can be easily hardcoded in the within the `main()` function of the `app.py` script, as below:

```python
def main():
    #sc, path = fetch_inputs()  # define spacecraft and TLE from user inputs
    sc = 'AEOLUS'
    path = None
    instantiate_globals(sc, tle_file=path)
    app.layout = serve_layout
    app.run_server()
```
## ⚙️ Configuration options
Later...