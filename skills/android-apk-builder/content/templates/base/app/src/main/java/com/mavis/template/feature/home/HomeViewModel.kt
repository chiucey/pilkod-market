package @PACKAGE_PATH@.feature.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import @PACKAGE_PATH@.data.SettingsRepo
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class HomeViewModel(private val repo: SettingsRepo) : ViewModel() {

    val userName = repo.userName.stateIn(
        viewModelScope, SharingStarted.WhileSubscribed(5_000), ""
    )

    fun onGreet() {
        // Placeholder action. Wire to your feature logic.
    }

    fun saveName(name: String) {
        viewModelScope.launch { repo.setUserName(name) }
    }
}
