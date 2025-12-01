from flask import Flask, render_template, request, redirect, url_for
from varasto import Varasto

app = Flask(__name__)

# In-memory storage for warehouses
varastot = {}
next_id = 1


def get_next_id():
    """Get the next unique ID for a warehouse."""
    global next_id
    current_id = next_id
    next_id += 1
    return current_id


@app.route("/")
def index():
    """List all warehouses."""
    return render_template("index.html", varastot=varastot)


@app.route("/varastot", methods=["POST"])
def create_varasto():
    """Create a new warehouse."""
    tilavuus = request.form.get("tilavuus", type=float)
    alku_saldo = request.form.get("alku_saldo", 0, type=float)
    nimi = request.form.get("nimi", "").strip()

    if tilavuus is None or tilavuus <= 0:
        return redirect(url_for("index"))

    varasto_id = get_next_id()
    varastot[varasto_id] = {
        "id": varasto_id,
        "nimi": nimi if nimi else f"Varasto {varasto_id}",
        "varasto": Varasto(tilavuus, alku_saldo),
    }
    return redirect(url_for("index"))


@app.route("/varastot/<int:varasto_id>")
def view_varasto(varasto_id):
    """View details of a specific warehouse."""
    if varasto_id not in varastot:
        return redirect(url_for("index"))
    return render_template("varasto.html", data=varastot[varasto_id])


@app.route("/varastot/<int:varasto_id>/muokkaa", methods=["GET", "POST"])
def edit_varasto(varasto_id):
    """Edit a warehouse."""
    if varasto_id not in varastot:
        return redirect(url_for("index"))

    if request.method == "POST":
        nimi = request.form.get("nimi", "").strip()
        tilavuus = request.form.get("tilavuus", type=float)

        if nimi:
            varastot[varasto_id]["nimi"] = nimi
        if tilavuus is not None and tilavuus > 0:
            old_varasto = varastot[varasto_id]["varasto"]
            new_varasto = Varasto(tilavuus, old_varasto.saldo)
            varastot[varasto_id]["varasto"] = new_varasto

        return redirect(url_for("view_varasto", varasto_id=varasto_id))

    return render_template("muokkaa.html", data=varastot[varasto_id])


@app.route("/varastot/<int:varasto_id>/lisaa", methods=["POST"])
def add_to_varasto(varasto_id):
    """Add items to a warehouse."""
    if varasto_id not in varastot:
        return redirect(url_for("index"))

    maara = request.form.get("maara", type=float)
    if maara is not None and maara > 0:
        varastot[varasto_id]["varasto"].lisaa_varastoon(maara)

    return redirect(url_for("view_varasto", varasto_id=varasto_id))


@app.route("/varastot/<int:varasto_id>/ota", methods=["POST"])
def take_from_varasto(varasto_id):
    """Remove items from a warehouse."""
    if varasto_id not in varastot:
        return redirect(url_for("index"))

    maara = request.form.get("maara", type=float)
    if maara is not None and maara > 0:
        varastot[varasto_id]["varasto"].ota_varastosta(maara)

    return redirect(url_for("view_varasto", varasto_id=varasto_id))


@app.route("/varastot/<int:varasto_id>/poista", methods=["POST"])
def delete_varasto(varasto_id):
    """Delete a warehouse."""
    if varasto_id in varastot:
        del varastot[varasto_id]
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
