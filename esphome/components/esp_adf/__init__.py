import esphome.config_validation as cv
import esphome.codegen as cg

from esphome.components import esp32

from esphome.const import CONF_ID

# CONFLICTS_WITH = ["i2s_audio"]
DEPENDENCIES = ["esp32"]

CONF_ESP_ADF_ID = "esp_adf_id"

esp_adf_ns = cg.esphome_ns.namespace("esp_adf")
ESPADF = esp_adf_ns.class_("ESPADF", cg.Component)
ESPADFPipeline = esp_adf_ns.class_("ESPADFPipeline", cg.Parented.template(ESPADF))

SUPPORTED_BOARDS = {"esp32s3box": "CONFIG_ESP32_S3_BOX_BOARD"}


def _validate_board(config):
    board = esp32.get_board()
    if board not in SUPPORTED_BOARDS:
        raise cv.Invalid(f"Board {board} is not supported by esp-adf")
    return config


CONFIG_SCHEMA = cv.All(
    cv.Schema({cv.GenerateID(): cv.declare_id(ESPADF)}),
    _validate_board,
    cv.only_with_esp_idf,
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    cg.add_define("USE_ESP_ADF")

    cg.add_platformio_option("build_unflags", "-Wl,--end-group")

    esp32.add_idf_component(
        name="esp-adf",
        repo="https://github.com/espressif/esp-adf",
        path="components",
        ref="v2.5",
        components=["*"],
        submodules=["components/esp-sr", "components/esp-adf-libs"],
    )

    esp32.add_idf_component(
        name="esp-dsp",
        repo="https://github.com/espressif/esp-dsp",
        ref="v1.2.0",
    )

    cg.add_platformio_option(
        "board_build.embed_txtfiles", "components/dueros_service/duer_profile"
    )
    esp32.add_idf_sdkconfig_option(SUPPORTED_BOARDS[esp32.get_board()], True)
