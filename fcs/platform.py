"""Campus page entry point; feature APIs live in separate modules."""

from flask import Blueprint, render_template

platform = Blueprint("platform", __name__)


@platform.get("/campus")
def campus():
    return render_template("campus.html")
