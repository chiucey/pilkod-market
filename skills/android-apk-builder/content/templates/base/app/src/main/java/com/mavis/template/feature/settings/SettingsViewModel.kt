package @PACKAGE_PATH@.feature.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import @PACKAGE_PATH@.data.SettingsRepo
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class SettingsViewModel(private val repo: SettingsRepo) : ViewModel() {
    val darkOverride = repo.darkOverride.stateIn(
        viewModelScope, SharingStarted.WhileSubscribed(5_000), null
    )

    fun setDarkOverride(value: Boolean?) {
        viewModelScope.launch { repo.setDarkOverride(value) }
    }
}
