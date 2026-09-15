from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# ==================== ANTI-TAMPER WRAPPER ====================
# Dựa trên kỹ thuật từ lyric0x10/Lua-Obfuscator:
# Phát hiện debug hook, xác minh tính toàn vẹn hàm.
ANTI_TAMPER = """local _g = getfenv or function() return _ENV end
local _d = _g().debug
local _h = _d and _d.sethook
local _c = 0
local function _tick() _c = _c + 1 end
if _h then
    _h(_tick, "l", 5)
    _tick()
    _tick()
    _h()
end
if _c < 2 then
    while true do end
end
"""

def obfuscate_lua(code, options):
    """Obfuscate Lua voi anti-tamper."""

    lines = code.split(chr(10))
    result = []

    # Tầng 1: Anti-tamper
    if options.get('antiTamper', True):
        result.append("-- Anti-Tamper Layer")
        result.append(ANTI_TAMPER)
        result.append("")

    # Tầng 2: Wrap code trong function
    result.append("local __protected = function()")
    for line in lines:
        result.append("    " + line)
    result.append("end")
    result.append("__protected()")

    output = chr(10).join(result)
    return output


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/obfuscate", methods=["POST"])
def api_obfuscate():
    try:
        data = request.get_json()
        code = data.get("code", "").strip()
        options = data.get("options", {})

        if not code:
            return jsonify({"ok": False, "error": "Vui long nhap code!"})

        output = obfuscate_lua(code, options)
        return jsonify({"ok": True, "output": output})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
